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


def generate_post_signature(caption: str, photos: List[str]) -> str:
    content = caption + "".join(photos)
    return hashlib.md5(content.encode("utf-8")).hexdigest()


def generate_post_id(caption: str, photos: List[str]) -> str:
    """Short 8-char hex ID derived from post content."""
    return generate_post_signature(caption, photos)[:8]


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


# ---------------------------------------------------------------------------
# Core scraper
# ---------------------------------------------------------------------------
def scrape_facebook_page(
    url: str,
    imgbb_api_key: str,
    target_post_count: int = 7,
    max_scrolls: int = 30,
) -> List[Dict[str, Any]]:
    posts_data: List[Dict[str, Any]] = []
    seen_signatures: Set[str] = set()

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
                            signature = generate_post_signature(caption, processed_photos)

                            if signature not in seen_signatures:
                                posts_data.append(
                                    {
                                        "id": generate_post_id(caption, processed_photos),
                                        "caption": caption,
                                        "photos": processed_photos,
                                        "scraped_at": datetime.now().isoformat(timespec="seconds"),
                                    }
                                )
                                seen_signatures.add(signature)
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
def save_to_json(posts: List[Dict[str, Any]], output_path: str = OUTPUT_FILE) -> None:
    """Write scraped posts to a JSON file, creating directories if needed."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(posts, f, indent=4, ensure_ascii=False)
    print(f"\n[SAVED] {len(posts)} posts written to {output_path}")


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    start_time = time.time()

    results = scrape_facebook_page(
        FACEBOOK_PAGE_URL,
        imgbb_api_key=IMGBB_API_KEY,
        target_post_count=TARGET_POSTS,
        max_scrolls=MAX_SCROLLS,
    )

    print("\n" + "=" * 50)
    print(f"EXTRACTION COMPLETE IN {time.time() - start_time:.2f} SECONDS")
    print("=" * 50 + "\n")

    save_to_json(results)
    print(json.dumps(results, indent=4, ensure_ascii=False))
