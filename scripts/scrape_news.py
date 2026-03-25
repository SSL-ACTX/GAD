"""
scrape_news.py — Facebook Page Scraper Module for GAD News

Scrapes the latest posts from the MGADO Facebook page, uploads images
to ImgBB (proxied via wsrv.nl), and saves the results to data/news.json.

Usage:
    python scripts/scrape_news.py
"""

import time
import random
import json
import hashlib
import os
import requests
import concurrent.futures
from datetime import datetime
from typing import List, Dict, Any, Set
from playwright.sync_api import sync_playwright, Route

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FACEBOOK_PAGE_URL = "https://www.facebook.com/MontalbanGenderAndDevelopment"
IMGBB_API_KEY = "768e4e92399d79e0b981a3368fe9a046"
TARGET_POSTS = 7
MAX_SCROLLS = 30

# Resolve paths relative to project root (one level up from scripts/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "news.json")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_delay(min_seconds: float = 1.0, max_seconds: float = 2.5) -> None:
    time.sleep(random.uniform(min_seconds, max_seconds))


import re
from datetime import timedelta

# Patterns that indicate Facebook alt text, NOT a date
_ALT_TEXT_PATTERNS = re.compile(
    r"May be|image of|photo of|text that says|No photo description",
    re.IGNORECASE,
)

# Month names for validation
_MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
_MONTH_ABBR = [m[:3] for m in _MONTHS]


def _looks_like_date(text: str) -> bool:
    """Return True only if text is short and looks like a date, not alt text."""
    if not text or len(text) > 60:
        return False
    if _ALT_TEXT_PATTERNS.search(text):
        return False
    # Must match one of: month name, relative time, or numeric patterns
    t = text.lower().strip()
    if any(m.lower() in t for m in _MONTHS + _MONTH_ABBR):
        return True
    if re.match(r"^\d+[hms]\s*(ago)?$", t):       # "2h", "30m", "5s"
        return True
    if re.match(r"^\d+d\s*(ago)?$", t):            # "3d"
        return True
    if t in ("just now", "yesterday", "today"):
        return True
    if re.match(r"^\d{1,2}/\d{1,2}/\d{2,4}$", t): # "3/10/2026"
        return True
    return False


def normalize_fb_date(raw: str) -> str:
    """Convert Facebook date text to a clean date string.

    Handles:
      - 'yesterday' -> '2026-03-16'
      - '2h' / '30m' / 'just now' / 'today' -> today's date
      - '3d' -> 3 days ago
      - 'March 10 at 10:30 AM' -> 'March 10, 2026'
      - 'March 10' (no year) -> adds current year
    """
    now = datetime.now()
    t = raw.strip().lower()

    if not t:
        return ""

    # Relative: just now / today
    if t in ("just now", "today"):
        return now.strftime("%B %d, %Y")

    # Relative: yesterday
    if t == "yesterday":
        return (now - timedelta(days=1)).strftime("%B %d, %Y")

    # Relative: Nh, Nm, Ns
    m = re.match(r"^(\d+)\s*([hms])", t)
    if m:
        return now.strftime("%B %d, %Y")

    # Relative: Nd (days ago)
    m = re.match(r"^(\d+)\s*d", t)
    if m:
        days = int(m.group(1))
        return (now - timedelta(days=days)).strftime("%B %d, %Y")

    # "March 10 at 10:30 AM" -> "March 10, 2026"
    m = re.match(r"^([A-Za-z]+ \d{1,2})\s+at\s+", raw.strip())
    if m:
        date_part = m.group(1)
        return f"{date_part}, {now.year}"

    # "March 10" (no year, no time)
    m = re.match(r"^([A-Za-z]+ \d{1,2})$", raw.strip())
    if m:
        return f"{m.group(1)}, {now.year}"

    # Already looks complete (e.g. "March 10, 2026")
    return raw.strip()


def generate_post_signature(caption: str, photos: List[str]) -> str:
    content = caption + "".join(photos)
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def generate_caption_hash(caption: str) -> str:
    """Hash based on caption text only — stable across re-scrapes."""
    return hashlib.md5(caption.strip().encode("utf-8")).hexdigest()[:8]


def load_existing_news(path: str = None) -> Dict[str, Dict[str, Any]]:
    """Load existing news.json and return a dict keyed by caption hash."""
    if path is None:
        path = OUTPUT_FILE
    try:
        with open(path, "r", encoding="utf-8") as f:
            items = json.load(f)
        return {item["id"]: item for item in items if isinstance(item, dict) and "id" in item}
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def upload_to_imgbb(image_url: str, api_key: str, expiration: int = 604800) -> str:
    """
    Uploads an image URL to ImgBB and returns the direct link.
    Expiration is set to 7 days (604800 seconds) by default.
    """
    try:
        url = "https://api.imgbb.com/1/upload"
        payload = {"key": api_key, "image": image_url, "expiration": expiration}
        response = requests.post(url, data=payload, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data["data"]["url"]
        else:
            print(f"   -> [ImgBB Error] Status {response.status_code}: {response.text}")
            return ""
    except Exception as e:
        print(f"   -> [ImgBB Error] Exception occurred: {e}")
        return ""


def fetch_post_og_image_via_playwright(context, url: str, timeout: int = 20000) -> str:
    """Try to fetch the post's og:image from the Facebook post page using Playwright.

    This is intended as a fallback when the post has no <img> tags (e.g., video posts).
    """
    try:
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout)
        # Wait for the page to stabilize (may be heavy but needed for OG meta to be present)
        page.wait_for_timeout(1500)
        og_image = page.locator('meta[property="og:image"]').first.get_attribute("content")
        page.close()
        return og_image or ""
    except Exception as e:
        print(f"   -> [OG Image] Failed to fetch og:image for {url}: {e}")
        try:
            page.close()
        except Exception:
            pass
        return ""


# ---------------------------------------------------------------------------
# Core scraper
# ---------------------------------------------------------------------------
def scrape_facebook_page(
    url: str,
    imgbb_api_key: str,
    target_post_count: int = 7,
    max_scrolls: int = 30,
    existing_posts: Dict[str, Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    posts_data: List[Dict[str, Any]] = []
    seen_signatures: Set[str] = set()
    # Allows de-duping by URL in case a post is processed multiple times.
    url_to_index: Dict[str, int] = {}
    if existing_posts is None:
        existing_posts = {}

    with sync_playwright() as p:
        print("[STATUS] Initializing stealth environment...")
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-features=IsolateOrigins,site-per-process",
            ],
        )

        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US",
            timezone_id="Asia/Manila",
        )

        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
            Object.defineProperty(navigator, 'hardwareConcurrency', { get: () => 8 });
            Object.defineProperty(navigator, 'deviceMemory', { get: () => 8 });
            const originalQuery = window.navigator.permissions.query;
            window.navigator.permissions.query = (parameters) => (
                parameters.name === 'notifications' ?
                    Promise.resolve({ state: Notification.permission }) :
                    originalQuery(parameters)
            );
        """)

        page = context.new_page()

        def block_heavy_resources(route: Route) -> None:
            if route.request.resource_type in ["image", "media", "font"]:
                route.abort()
            else:
                route.continue_()

        page.route("**/*", block_heavy_resources)

        try:
            print(f"[ACTION] Navigating to {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            random_delay(3, 5)

            scroll_attempts = 0
            processed_index = 0

            print(f"[STATUS] Engaging dynamic extraction protocol. Target: {target_post_count} posts.")

            while len(posts_data) < target_post_count and scroll_attempts < max_scrolls:

                # Standard UI overlay dismissal
                try:
                    close_btns = page.locator('div[aria-label="Close"], div[aria-label="close"]')
                    for i in range(close_btns.count()):
                        if close_btns.nth(i).is_visible():
                            close_btns.nth(i).click(force=True)
                            print("[ACTION] Cleared standard UI overlay.")
                            page.wait_for_timeout(1000)
                except Exception:
                    pass

                current_count = page.locator('div[role="article"]').count()

                if processed_index >= current_count:
                    print(f"[ACTION] Bypassing scroll locks and advancing... (Attempt {scroll_attempts+1}/{max_scrolls})")
                    page.evaluate("""
                        document.querySelectorAll('[role="dialog"]').forEach(dialog => {
                            dialog.style.setProperty('display', 'none', 'important');
                            dialog.style.setProperty('opacity', '0', 'important');
                            dialog.style.setProperty('pointer-events', 'none', 'important');
                        });
                        const loginForms = document.querySelectorAll('form[action*="/login/"]');
                        loginForms.forEach(form => {
                            let currentElement = form;
                            for (let i = 0; i < 4; i++) {
                                if (currentElement && currentElement.style) {
                                    currentElement.style.setProperty('display', 'none', 'important');
                                    currentElement.style.setProperty('pointer-events', 'none', 'important');
                                }
                                if (currentElement) {
                                    currentElement = currentElement.parentElement;
                                }
                            }
                        });
                        document.querySelectorAll('div').forEach(el => {
                            const style = window.getComputedStyle(el);
                            if (style.position === 'fixed' || style.position === 'absolute') {
                                if (parseInt(style.zIndex) > 50 || el.innerText.trim() === '') {
                                    el.style.setProperty('display', 'none', 'important');
                                    el.style.setProperty('pointer-events', 'none', 'important');
                                    el.style.setProperty('opacity', '0', 'important');
                                }
                            }
                        });
                        document.body.style.setProperty('overflow', 'auto', 'important');
                        document.documentElement.style.setProperty('overflow', 'auto', 'important');
                    """)

                    page.wait_for_timeout(500)
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(500)
                    page.keyboard.press("PageDown")
                    page.wait_for_timeout(500)
                    page.keyboard.press("PageDown")
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight);")

                    random_delay(2.5, 4.0)
                    scroll_attempts += 1
                    continue

                for i in range(processed_index, current_count):
                    if len(posts_data) >= target_post_count:
                        break

                    print(f"[STATUS] Analyzing post node {i+1}...")
                    article = page.locator('div[role="article"]').nth(i)

                    try:
                        article.scroll_into_view_if_needed()
                        page.wait_for_timeout(500)

                        see_more = article.locator(
                            'div[role="button"]:has-text("See more"), div[role="button"]:has-text("See More")'
                        )
                        if see_more.count() > 0:
                            print("   -> Forcing text expansion...")
                            see_more.first.evaluate("node => node.click()")
                            page.wait_for_timeout(800)

                        caption = ""
                        msg_locator = article.locator('div[data-ad-preview="message"]')
                        if msg_locator.count() > 0:
                            caption = msg_locator.first.inner_text().strip()

                        # --- Extract post URL ---
                        post_url = ""
                        try:
                            # Look for permalink-style links (timestamps that link to the post)
                            link_locator = article.locator('a[href*="/posts/"], a[href*="/photos/"], a[href*="pfbid"], a[href*="/permalink/"]')
                            if link_locator.count() > 0:
                                href = link_locator.first.get_attribute("href") or ""
                                if href.startswith("/"):
                                    post_url = f"https://www.facebook.com{href}"
                                elif href.startswith("http"):
                                    post_url = href.split("?")[0]  # strip tracking params
                        except Exception:
                            pass

                        # --- Extract post date ---
                        post_date = ""
                        try:
                            # Strategy 1: direct text inside permalink-style timestamp links
                            time_links = article.locator('a[href*="/posts/"], a[href*="pfbid"], a[href*="/permalink/"]')
                            for tl in range(min(time_links.count(), 5)):
                                link_el = time_links.nth(tl)
                                # Check the link's own direct text first
                                link_text = link_el.inner_text().strip()
                                if _looks_like_date(link_text):
                                    post_date = link_text
                                    break
                                # Check immediate child spans (skip deeply nested img alt text)
                                direct_spans = link_el.locator('> span')
                                for s in range(min(direct_spans.count(), 3)):
                                    span_text = direct_spans.nth(s).inner_text().strip()
                                    if _looks_like_date(span_text):
                                        post_date = span_text
                                        break
                                if post_date:
                                    break

                            # Strategy 2: aria-label on links containing month names
                            if not post_date:
                                date_link = article.locator('a[aria-label]')
                                for d in range(min(date_link.count(), 5)):
                                    label = date_link.nth(d).get_attribute("aria-label") or ""
                                    if _looks_like_date(label):
                                        post_date = label
                                        break

                            # Normalize to clean date format
                            if post_date:
                                post_date = normalize_fb_date(post_date)

                        except Exception:
                            pass

                        # --- Check if post already exists (skip image upload) ---
                        caption_id = generate_caption_hash(caption) if caption else ""

                        if caption_id and caption_id in existing_posts:
                            existing = existing_posts[caption_id]
                            print(f"   -> [CACHED] Post already exists, reusing images.")

                            cached_photos = existing.get("photos", []) or []
                            # If cached entry had no images, try to fetch a thumbnail now.
                            if not cached_photos and post_url:
                                print("   -> [CACHED] No cached images; attempting thumbnail fallback.")
                                og_img = fetch_post_og_image_via_playwright(context, post_url)
                                if og_img:
                                    clean_imgbb_url = upload_to_imgbb(og_img, imgbb_api_key)
                                    if clean_imgbb_url:
                                        cached_photos = [f"https://wsrv.nl/?url={clean_imgbb_url}&maxage=7d"]
                                        print(f"   -> [CACHED] Saved fallback thumbnail: {cached_photos[0]}")

                            updated = {
                                "id": caption_id,
                                "caption": caption,
                                "photos": cached_photos,
                                "post_url": post_url or existing.get("post_url", ""),
                                "post_date": post_date or existing.get("post_date", ""),
                                "scraped_at": existing.get("scraped_at", datetime.now().isoformat(timespec="seconds")),
                            }
                            if post_url and post_url in url_to_index:
                                idx = url_to_index[post_url]
                                existing_entry = posts_data[idx]
                                # Merge photos if we got new ones
                                if not existing_entry.get("photos") and cached_photos:
                                    existing_entry["photos"] = cached_photos
                                existing_entry["scraped_at"] = updated["scraped_at"]
                                print(f"[SUCCESS] Updated cached entry for URL (deduped). Progress: {len(posts_data)}/{target_post_count}")
                            elif caption_id not in seen_signatures:
                                posts_data.append(updated)
                                seen_signatures.add(caption_id)
                                if post_url:
                                    url_to_index[post_url] = len(posts_data) - 1
                                print(f"[SUCCESS] Data acquired (cached). Progress: {len(posts_data)}/{target_post_count}")
                            else:
                                print("   -> Discarded (Duplicate hash).")
                            processed_index += 1
                            continue

                        raw_photos = []
                        processed_photos = []
                        images = article.locator("img").all()

                        for img in images:
                            src = img.get_attribute("src") or ""
                            alt = img.get_attribute("alt") or ""
                            width = img.get_attribute("width")

                            if not src:
                                continue
                            if any(x in src for x in ["emoji.php", "/rsrc.php/", "tracking"]):
                                continue
                            if any(x in alt.lower() for x in ["profile picture", "cover photo"]):
                                continue
                            if width and width.isdigit() and int(width) < 100:
                                continue

                            raw_photos.append(src)

                        if not raw_photos and post_url:
                            print("   -> [INFO] No images found; trying to fetch og:image thumbnail via Playwright.")
                            og_img = fetch_post_og_image_via_playwright(context, post_url)
                            if og_img:
                                raw_photos.append(og_img)

                        if raw_photos:
                            print(f"   -> [Batch] Transferring {len(raw_photos)} images to ImgBB...")

                            def process_single_image(fb_src: str) -> str:
                                clean_imgbb_url = upload_to_imgbb(fb_src, imgbb_api_key)
                                if clean_imgbb_url:
                                    return f"https://wsrv.nl/?url={clean_imgbb_url}&maxage=7d"
                                return fb_src

                            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                                processed_photos = list(executor.map(process_single_image, raw_photos))

                        if caption or processed_photos:
                            post_id = caption_id if caption_id else generate_post_signature(caption, processed_photos)[:8]

                            if post_url and post_url in url_to_index:
                                idx = url_to_index[post_url]
                                existing_entry = posts_data[idx]
                                # Merge any newly found photos
                                if not existing_entry.get("photos") and processed_photos:
                                    existing_entry["photos"] = processed_photos
                                existing_entry["scraped_at"] = datetime.now().isoformat(timespec="seconds")
                                print(f"[SUCCESS] Updated existing entry for URL (deduped). Progress: {len(posts_data)}/{target_post_count}")
                            elif post_id not in seen_signatures:
                                posts_data.append(
                                    {
                                        "id": post_id,
                                        "caption": caption,
                                        "photos": processed_photos,
                                        "post_url": post_url,
                                        "post_date": post_date,
                                        "scraped_at": datetime.now().isoformat(timespec="seconds"),
                                    }
                                )
                                seen_signatures.add(post_id)
                                if post_url:
                                    url_to_index[post_url] = len(posts_data) - 1
                                print(f"[SUCCESS] Data acquired. Progress: {len(posts_data)}/{target_post_count}")
                            else:
                                print("   -> Discarded (Duplicate hash).")
                        else:
                            print("   -> Discarded (Empty payload).")

                    except Exception as e:
                        print(f"   -> [WARNING] Node failure: {e}")

                    processed_index += 1

        except Exception as e:
            print(f"\n[CRITICAL ERROR] Subroutine failed: {e}")

        finally:
            print("[STATUS] Terminating processes...")
            browser.close()

    return posts_data


# ---------------------------------------------------------------------------
# Save to JSON
# ---------------------------------------------------------------------------
def save_to_json(new_posts: List[Dict[str, Any]], output_path: str = OUTPUT_FILE) -> None:
    """Merge newly scraped posts with existing ones and save to JSON.
    
    This ensures data persistence by prepending new findings to the top
    and keeping all previously scraped items that weren't updated in this run.
    """
    # 1. Load ALL existing posts from the file to handle history
    try:
        if os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as f:
                all_posts = json.load(f)
                if not isinstance(all_posts, list):
                    all_posts = []
        else:
            all_posts = []
    except (json.JSONDecodeError, IOError):
        all_posts = []

    # 2. Identify IDs that were just refreshed or added
    found_ids = {p["id"] for p in new_posts if isinstance(p, dict) and "id" in p}
    
    # 3. Preserve historical posts that were NOT in the current scrape
    # This keeps the history alive and avoids duplicates.
    preserved_posts = [p for p in all_posts if isinstance(p, dict) and p.get("id") not in found_ids]
    
    # 4. Final list: Current results (newest first) + historical remainder
    merged_results = new_posts + preserved_posts
    
    # 5. Write back to disk
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(merged_results, f, indent=4, ensure_ascii=False)
    
    newly_added = len(found_ids) - (len(all_posts) - len(preserved_posts))
    
    print(f"\n[SAVED] Persistence sync complete:")
    print(f"   -> Scraped/Updated in this session: {len(new_posts)}")
    print(f"   -> Preserved from history: {len(preserved_posts)}")
    print(f"   -> Total records now: {len(merged_results)}")
    print(f"   -> Destination: {output_path}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    start_time = time.time()

    # Load existing data to avoid re-uploading images
    existing = load_existing_news()
    if existing:
        print(f"[INFO] Loaded {len(existing)} existing posts from cache.")

    results = scrape_facebook_page(
        FACEBOOK_PAGE_URL,
        imgbb_api_key=IMGBB_API_KEY,
        target_post_count=TARGET_POSTS,
        max_scrolls=MAX_SCROLLS,
        existing_posts=existing,
    )

    print("\n" + "=" * 50)
    print(f"EXTRACTION COMPLETE IN {time.time() - start_time:.2f} SECONDS")
    print("=" * 50 + "\n")

    save_to_json(results)
    print(json.dumps(results, indent=4, ensure_ascii=False))
