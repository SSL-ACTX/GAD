// Toggle Mobile Menu
const menuBtn = document.getElementById('mobile-menu-btn');
const navMenu = document.getElementById('nav-menu');
const menuIcon = document.getElementById('menu-icon');

menuBtn.addEventListener('click', () => {
    navMenu.classList.toggle('hidden');
    navMenu.classList.toggle('mobile-menu-active');
            
    // Toggle icon between bars and X
    if (navMenu.classList.contains('hidden')) {
        menuIcon.classList.replace('fa-times', 'fa-bars');
    } else {
        menuIcon.classList.replace('fa-bars', 'fa-times');
    }
});

// Handle Dropdowns on Mobile
const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
const dropdownSubToggles = document.querySelectorAll('.dropdown-toggle-sub');

dropdownToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
            e.preventDefault();
            const submenu = toggle.nextElementSibling;
            submenu.classList.toggle('hidden');
            // Optional: Rotate arrow
            toggle.querySelector('i').classList.toggle('rotate-180');
        }
    });
});

dropdownSubToggles.forEach(toggle => {
    toggle.addEventListener('click', (e) => {
        if (window.innerWidth < 1024) {
            e.preventDefault();
            const submenu = toggle.nextElementSibling;
            submenu.classList.toggle('hidden');
        }
    });
});

// --- ACCESSIBILITY: HIGH CONTRAST ---
const accessibilityBtn = document.getElementById('accessibility-toggle');
const body = document.body;

// Check for saved preference
if (localStorage.getItem('high-contrast') === 'enabled') {
    body.classList.add('high-contrast');
}

accessibilityBtn.addEventListener('click', () => {
    body.classList.toggle('high-contrast');
    
    // Save preference
    if (body.classList.contains('high-contrast')) {
        localStorage.setItem('high-contrast', 'enabled');
    } else {
        localStorage.setItem('high-contrast', 'disabled');
    }
});

// --- ACCESSIBILITY TOOLS LOGIC ---
const a11yIcon = document.getElementById('accessibility-toggle');
const a11yPanel = document.getElementById('accessibility-panel');
const closeA11y = document.getElementById('close-a11y');
const resetA11y = document.getElementById('reset-a11y');

a11yIcon.addEventListener('click', () => a11yPanel.classList.add('open'));
closeA11y.addEventListener('click', () => a11yPanel.classList.remove('open'));

function setupA11yToggle(btnId, className) {
    const btn = document.getElementById(btnId);
    if (localStorage.getItem(className) === 'true') {
        document.body.classList.add(className);
        btn.classList.add('bg-active');
    }
    btn.addEventListener('click', () => {
        const isActive = document.body.classList.toggle(className);
        btn.classList.toggle('bg-active');
        localStorage.setItem(className, isActive);
    });
}

setupA11yToggle('btn-contrast', 'a11y-contrast');
setupA11yToggle('btn-grayscale', 'a11y-grayscale');
setupA11yToggle('btn-links', 'a11y-underline-links');

resetA11y.addEventListener('click', () => {
    ['a11y-contrast', 'a11y-grayscale', 'a11y-underline-links'].forEach(cls => {
        document.body.classList.remove(cls);
        const type = cls.split('-')[1];
        document.getElementById('btn-' + type).classList.remove('bg-active');
        localStorage.removeItem(cls);
    });
});

// --- FONT SIZE SCALER ---
const fontBtn = document.getElementById('font-size-toggle');
const fontSizes = ['100%', '110%', '120%'];
let sizeIdx = parseInt(localStorage.getItem('fontSizeIdx')) || 0;
document.documentElement.style.fontSize = fontSizes[sizeIdx];

fontBtn.addEventListener('click', () => {
    sizeIdx = (sizeIdx + 1) % fontSizes.length;
    document.documentElement.style.fontSize = fontSizes[sizeIdx];
    localStorage.setItem('fontSizeIdx', sizeIdx);
});