// --- MOBILE MENU ---
const menuBtn = document.getElementById('mobile-menu-btn');
const navMenu = document.getElementById('nav-menu');
const menuIcon = document.getElementById('menu-icon');

if (menuBtn) {
    menuBtn.addEventListener('click', () => {
        navMenu.classList.toggle('hidden');
        menuIcon.classList.toggle('fa-bars');
        menuIcon.classList.toggle('fa-times');
    });
}

// --- MOBILE DROPDOWNS ---
document.querySelectorAll('.dropdown-toggle, .dropdown-toggle-sub').forEach(btn => {
    btn.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
            e.preventDefault();
            const menu = btn.nextElementSibling;
            if (menu) menu.classList.toggle('hidden');
        }
    });
});

// --- LIVE SEARCH SUGGESTIONS ---
const searchInput = document.getElementById('search-input');
const suggestionBox = document.getElementById('suggestion-box');

if (searchInput && suggestionBox) {
    searchInput.addEventListener('input', async (e) => {
        const query = e.target.value.trim();
        if (query.length < 2) {
            suggestionBox.classList.add('hidden');
            return;
        }

        try {
            const response = await fetch(`/api/suggestions?q=${encodeURIComponent(query)}`);
            const suggestions = await response.json();

            if (suggestions.length > 0) {
                suggestionBox.innerHTML = suggestions.map(text => `
                    <div class="suggestion-item px-4 py-3 hover:bg-[#006837] cursor-pointer text-xs font-semibold border-b border-white/5 last:border-0 transition-colors">
                        ${text}
                    </div>
                `).join('');
                suggestionBox.classList.remove('hidden');
            } else {
                suggestionBox.classList.add('hidden');
            }
        } catch (err) { console.error(err); }
    });

    suggestionBox.addEventListener('click', (e) => {
        const item = e.target.closest('.suggestion-item');
        if (item) {
            searchInput.value = item.innerText.trim();
            suggestionBox.classList.add('hidden');
            searchInput.closest('form').submit();
        }
    });

    document.addEventListener('click', (e) => {
        if (!searchInput.contains(e.target) && !suggestionBox.contains(e.target)) {
            suggestionBox.classList.add('hidden');
        }
    });
}

// --- ACCESSIBILITY MENU ---
const a11yMenuBtn = document.getElementById('a11y-menu-btn');
const a11yMenu = document.getElementById('a11y-menu');
const a11yCloseBtn = document.getElementById('a11y-close');
const a11yResetBtn = document.getElementById('a11y-reset-all');

const a11yToggles = document.querySelectorAll('.a11y-toggle');
const textInc = document.getElementById('a11y-text-inc');
const textDec = document.getElementById('a11y-text-dec');
const textReset = document.getElementById('a11y-text-reset');
const quickTextBtn = document.getElementById('a11y-quick-text-btn');

let currentTextZoom = 100;

function updateA11yState() {
    const isHighContrast = document.body.classList.contains('high-contrast');
    const isInvert = document.body.classList.contains('invert-colors');

    a11yToggles.forEach(btn => {
        const action = btn.dataset.action;
        const iconContainer = btn.querySelector('div.w-8');
        const isActive = (action === 'contrast' && isHighContrast) || (action === 'invert' && isInvert);

        if (isActive) {
            btn.classList.add('bg-primary-green', 'text-white');
            btn.classList.remove('hover:bg-green-50');
            btn.querySelector('p:last-child').classList.add('text-green-100');
            btn.querySelector('p:last-child').classList.remove('text-gray-500');
            iconContainer.classList.add('bg-white/20', 'text-white');
            iconContainer.classList.remove('bg-gray-100', 'text-gray-600');
        } else {
            btn.classList.remove('bg-primary-green', 'text-white');
            btn.classList.add('hover:bg-green-50');
            btn.querySelector('p:last-child').classList.add('text-gray-500');
            btn.querySelector('p:last-child').classList.remove('text-green-100');
            iconContainer.classList.remove('bg-white/20', 'text-white');
            iconContainer.classList.add('bg-gray-100', 'text-gray-600');
        }
    });

    document.documentElement.style.fontSize = `${currentTextZoom}%`;
    localStorage.setItem('a11y-contrast', isHighContrast);
    localStorage.setItem('a11y-invert', isInvert);
    localStorage.setItem('a11y-text-zoom', currentTextZoom);
}

// Load saved settings
if (localStorage.getItem('a11y-contrast') === 'true') document.body.classList.add('high-contrast');
if (localStorage.getItem('a11y-invert') === 'true') document.body.classList.add('invert-colors');
if (localStorage.getItem('a11y-text-zoom')) {
    currentTextZoom = parseInt(localStorage.getItem('a11y-text-zoom'));
    document.documentElement.style.fontSize = `${currentTextZoom}%`;
}
updateA11yState();

if (a11yMenuBtn && a11yMenu) {
    a11yMenuBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        a11yMenu.classList.toggle('hidden');
    });

    a11yCloseBtn.addEventListener('click', () => {
        a11yMenu.classList.add('hidden');
    });

    document.addEventListener('click', (e) => {
        if (!a11yMenu.contains(e.target) && !a11yMenuBtn.contains(e.target)) {
            a11yMenu.classList.add('hidden');
        }
    });

    a11yToggles.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.action;
            if (action === 'contrast') document.body.classList.toggle('high-contrast');
            if (action === 'invert') document.body.classList.toggle('invert-colors');
            updateA11yState();
        });
    });

    if (textInc) textInc.addEventListener('click', () => { currentTextZoom = Math.min(currentTextZoom + 10, 150); updateA11yState(); });
    if (textDec) textDec.addEventListener('click', () => { currentTextZoom = Math.max(currentTextZoom - 10, 80); updateA11yState(); });
    if (textReset) textReset.addEventListener('click', () => { currentTextZoom = 100; updateA11yState(); });

    if (quickTextBtn) quickTextBtn.addEventListener('click', () => {
        currentTextZoom = currentTextZoom >= 150 ? 100 : currentTextZoom + 10;
        updateA11yState();
    });

    if (a11yResetBtn) {
        a11yResetBtn.addEventListener('click', () => {
            document.body.classList.remove('high-contrast', 'invert-colors');
            currentTextZoom = 100;
            updateA11yState();
        });
    }
}

// --- FLOATING NAVIGATION BURGER (FAB) ---
const fabContainer = document.getElementById('floating-nav-container');
const fabBtn = document.getElementById('floating-nav-btn');
const fabOverlay = document.getElementById('fab-overlay');
const fabMenuWrapper = document.getElementById('fab-menu-container');
const scrollToTopFAB = document.getElementById('scrollToTopFAB');

if (fabBtn && fabOverlay) {
    // Show/Hide FAB on scroll
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            fabContainer.classList.add('visible');
        } else {
            fabContainer.classList.remove('visible');
        }
    });

    fabBtn.addEventListener('click', () => {
        const isOpen = !fabOverlay.classList.contains('translate-x-full');

        if (isOpen) {
            // Close
            fabOverlay.classList.add('translate-x-full');
            fabBtn.classList.remove('burger-active');
            fabMenuWrapper.classList.remove('fab-menu-active');
            document.body.style.overflow = '';
        } else {
            // Open
            fabOverlay.classList.remove('translate-x-full');
            fabBtn.classList.add('burger-active');
            setTimeout(() => {
                fabMenuWrapper.classList.add('fab-menu-active');
            }, 100);
            document.body.style.overflow = 'hidden';
        }
    });

    // Close on escape key
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && !fabOverlay.classList.contains('translate-x-full')) {
            fabBtn.click();
        }
    });
}

if (scrollToTopFAB) {
    scrollToTopFAB.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
        if (fabBtn && !fabOverlay.classList.contains('translate-x-full')) {
            fabBtn.click();
        }
    });
}
