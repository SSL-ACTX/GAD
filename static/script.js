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