// Main JavaScript for Mathura Darshan

// Utility Functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// API Helper
const API = {
    async get(url) {
        const response = await fetch(url);
        return response.json();
    },

    async post(url, data) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify(data)
        });
        return response.json();
    },

    async delete(url) {
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });
        return response.json();
    }
};

const BRIJ_TRANSLATIONS = {
    brand_title: 'मथुरा दर्शन',
    brand_subtitle: 'ब्रज यात्रा ऐप',
    nav_home: 'घर',
    nav_explore: 'घूमौ',
    nav_plan_trip: 'यात्रा बनायौ',
    nav_rush_calc: 'भीड़ देखौ',
    nav_timetable: 'समय सारिणी',
    nav_navigate: 'रास्तौ',
    nav_services: 'सेवाएं',
    nav_chat: 'बातचीत',
    nav_favorites: 'पसंदीदा',
    nav_profile: 'परिचय',
    nav_logout: 'बाहर जाओ',
    nav_login: 'अंदर आओ',
    nav_register: 'जुड़ौ',
    mobile_plan: 'योजना',
    translate_button: 'भाषा',
    all_languages: 'सब भाषाएं',
    theme_dark: 'गाढ़ा',
    theme_light: 'उजियारो',
    footer_about: 'परिचय',
    footer_about_text: 'मथुरा दर्शन मंदिर, घाट, त्योहार, भोजन अउर लोकल सेवाएं सरल ढंग सै देखै में मदद करै है।',
    footer_quick_links: 'फटाफट कड़ियां',
    footer_explore_places: 'जगह देखौ',
    footer_plan_trip: 'अपनी यात्रा बनायौ',
    footer_rush_calculator: 'भीड़ गणना',
    footer_timetable: 'मंदिर समय खोजौ',
    footer_ask_ai: 'एआई सै पूछौ',
    footer_contact: 'सम्पर्क',
    footer_rights: '© 2026 मथुरा दर्शन। सब हक सुरक्षित।',
};

// DOM Ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('Mathura Darshan app loaded');
    initializeApp();
});

function initializeApp() {
    initializeThemeToggle();
    initializeTranslationControls();
    initializeNavbarState();
    initializeMobileNavigation();
    initializeSmoothAnchors();
    initializeRevealAnimations();
    initializeImageLoading();
    initializeButtonFeedback();
    initializeFormPolish();

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeTranslationControls() {
    const widget = document.querySelector('.translate-widget');
    const toggle = document.querySelector('[data-translate-toggle]');
    const panel = document.querySelector('[data-translate-panel]');
    const select = document.querySelector('[data-translate-select]');

    document.querySelectorAll('[data-i18n-key]').forEach((element) => {
        if (!element.dataset.originalText) {
            element.dataset.originalText = element.textContent.trim();
        }
    });

    if (!widget || !toggle || !panel) {
        return;
    }

    const savedLanguage = localStorage.getItem('mathura-language') || 'en';

    toggle.addEventListener('click', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const isOpen = !panel.hasAttribute('hidden');
        panel.toggleAttribute('hidden', isOpen);
        toggle.setAttribute('aria-expanded', String(!isOpen));
    });

    panel.addEventListener('click', function (event) {
        event.stopPropagation();
    });

    document.addEventListener('click', function (event) {
        if (!widget.contains(event.target)) {
            panel.setAttribute('hidden', '');
            toggle.setAttribute('aria-expanded', 'false');
        }
    });

    document.querySelectorAll('[data-translate-lang]').forEach((button) => {
        button.addEventListener('click', function () {
            applyTranslationMode(button.dataset.translateLang);
            panel.setAttribute('hidden', '');
            toggle.setAttribute('aria-expanded', 'false');
        });
    });

    if (select) {
        select.value = savedLanguage;
        select.addEventListener('change', function () {
            applyTranslationMode(select.value);
            panel.setAttribute('hidden', '');
            toggle.setAttribute('aria-expanded', 'false');
        });
    }

    if (savedLanguage !== 'en') {
        window.setTimeout(() => applyTranslationMode(savedLanguage, { persist: false }), 300);
    } else {
        applyBrijChromeTranslations('en');
    }
}

function getBasePageUrl() {
    const url = new URL(window.location.href);
    url.searchParams.delete('translated');
    return url.toString();
}

function openTranslatedPage(language) {
    const sourceUrl = getBasePageUrl();

    if (language === 'en') {
        window.location.href = sourceUrl;
        return;
    }

    const translatedUrl = `https://translate.google.com/translate?sl=en&tl=${encodeURIComponent(language)}&u=${encodeURIComponent(sourceUrl)}`;
    window.location.href = translatedUrl;
}

function applyBrijChromeTranslations(mode) {
    const isBrij = mode === 'brij';
    document.documentElement.setAttribute('data-site-language', mode);

    document.querySelectorAll('[data-i18n-key]').forEach((element) => {
        const key = element.dataset.i18nKey;
        const originalText = element.dataset.originalText || element.textContent.trim();
        element.textContent = isBrij && BRIJ_TRANSLATIONS[key] ? BRIJ_TRANSLATIONS[key] : originalText;
    });
}

function applyTranslationMode(language, options = {}) {
    const { persist = true } = options;

    if (persist) {
        localStorage.setItem('mathura-language', language);
    }

    if (language === 'brij') {
        applyBrijChromeTranslations('brij');
        return;
    }

    applyBrijChromeTranslations('en');
    openTranslatedPage(language);
}

function initializeNavbarState() {
    const navbar = document.querySelector('.spiritual-navbar');
    if (!navbar) return;

    function updateNavbar() {
        navbar.classList.toggle('navbar-scrolled', window.scrollY > 12);
    }

    updateNavbar();
    window.addEventListener('scroll', updateNavbar, { passive: true });
}

function initializeSmoothAnchors() {
    document.querySelectorAll('a[href^="#"]:not([href="#"])').forEach(anchor => {
        anchor.addEventListener('click', function(event) {
            const target = document.querySelector(this.getAttribute('href'));
            if (!target) return;

            event.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });
}

function initializeMobileNavigation() {
    const navbarCollapse = document.getElementById('navbarNav');
    if (!navbarCollapse || typeof bootstrap === 'undefined') return;

    const collapseInstance = bootstrap.Collapse.getOrCreateInstance(navbarCollapse, { toggle: false });
    navbarCollapse.querySelectorAll('.nav-link').forEach((link) => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 991 && navbarCollapse.classList.contains('show')) {
                collapseInstance.hide();
            }
        });
    });
}

function initializeRevealAnimations() {
    const targets = document.querySelectorAll([
        '.app-hero',
        '.card',
        '.section-kicker',
        'main h1',
        'main h3',
        '.alert',
        '.nav-tabs'
    ].join(','));

    targets.forEach((element, index) => {
        element.classList.add('reveal-on-scroll');
        element.style.transitionDelay = `${Math.min(index * 35, 210)}ms`;
    });

    if (!('IntersectionObserver' in window)) {
        targets.forEach(element => element.classList.add('is-visible'));
        return;
    }

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    targets.forEach(element => observer.observe(element));
}

function initializeImageLoading() {
    document.querySelectorAll('img').forEach(img => {
        img.loading = img.loading || 'lazy';
        img.decoding = 'async';

        if (img.complete) {
            img.classList.add('image-loaded');
            return;
        }

        img.style.opacity = '0';
        img.style.transition = 'opacity 0.35s ease';
        img.addEventListener('load', () => {
            img.classList.add('image-loaded');
            img.style.opacity = '1';
        }, { once: true });
    });
}

function initializeButtonFeedback() {
    document.addEventListener('click', function(event) {
        const button = event.target.closest('.btn, .chip, .theme-toggle');
        if (!button) return;

        button.classList.remove('tap-feedback');
        void button.offsetWidth;
        button.classList.add('tap-feedback');
    });
}

function initializeFormPolish() {
    document.querySelectorAll('.form-control, .form-select').forEach(field => {
        field.addEventListener('input', function() {
            this.classList.toggle('has-value', Boolean(this.value));
        });
        field.classList.toggle('has-value', Boolean(field.value));
    });
}

function initializeThemeToggle() {
    const toggle = document.querySelector('[data-theme-toggle]');
    const root = document.documentElement;

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        localStorage.setItem('mathura-theme', theme);

        if (!toggle) return;

        const icon = toggle.querySelector('i');
        const label = toggle.querySelector('span');
        const isDark = theme === 'dark';

        if (icon) {
            icon.className = isDark ? 'bi bi-sun' : 'bi bi-moon-stars';
        }

        if (label) {
            const savedLanguage = localStorage.getItem('mathura-language') || 'en';
            label.textContent = isDark
                ? (savedLanguage === 'brij' ? BRIJ_TRANSLATIONS.theme_light : 'Light')
                : (savedLanguage === 'brij' ? BRIJ_TRANSLATIONS.theme_dark : 'Dark');
        }
    }

    applyTheme(localStorage.getItem('mathura-theme') || 'light');

    if (toggle) {
        toggle.addEventListener('click', function() {
            const nextTheme = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
            applyTheme(nextTheme);
        });
    }
}

// Distance Calculator (Haversine Formula)
function calculateDistance(lat1, lon1, lat2, lon2) {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
              Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
              Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
}

// Notification Handler
class NotificationManager {
    static show(message, type = 'info', duration = 3000) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.setAttribute('role', 'alert');
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.insertBefore(alertDiv, document.body.firstChild);
        
        if (duration) {
            setTimeout(() => alertDiv.remove(), duration);
        }
    }

    static success(message, duration = 3000) {
        this.show(message, 'success', duration);
    }

    static error(message, duration = 5000) {
        this.show(message, 'danger', duration);
    }

    static info(message, duration = 3000) {
        this.show(message, 'info', duration);
    }
}

// Form Validation
class FormValidator {
    static validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    static validatePhone(phone) {
        const re = /^[0-9]{10}$/;
        return re.test(phone.replace(/\D/g, ''));
    }

    static validatePassword(password) {
        return password.length >= 6;
    }
}

// Local Storage Helper
const Storage = {
    set(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    },

    get(key) {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : null;
    },

    remove(key) {
        localStorage.removeItem(key);
    },

    clear() {
        localStorage.clear();
    }
};

// Geolocation Helper
const Geolocation = {
    async getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject('Geolocation not supported');
            }
            navigator.geolocation.getCurrentPosition(
                position => resolve(position.coords),
                error => reject(error)
            );
        });
    },

    async getCoordinates() {
        try {
            const coords = await this.getCurrentPosition();
            return {
                lat: coords.latitude,
                lng: coords.longitude
            };
        } catch (error) {
            console.error('Geolocation error:', error);
            return null;
        }
    }
};

// Time/Date Utilities
const DateUtils = {
    formatDate(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleDateString('en-IN');
    },

    formatDateTime(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        return date.toLocaleString('en-IN');
    },

    getRelativeTime(date) {
        if (typeof date === 'string') {
            date = new Date(date);
        }
        const seconds = Math.floor((new Date() - date) / 1000);
        
        if (seconds < 60) return 'just now';
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
        if (seconds < 604800) return `${Math.floor(seconds / 86400)}d ago`;
        
        return this.formatDate(date);
    }
};

// Export for use in other scripts
window.API = API;
window.NotificationManager = NotificationManager;
window.FormValidator = FormValidator;
window.Storage = Storage;
window.Geolocation = Geolocation;
window.DateUtils = DateUtils;
