// Shared light/dark theme controller for all pages.
// Theme is applied as a `data-theme` attribute on <html>, which the CSS
// cascades from (see styles.css) so no per-element classes are needed.
(function () {
    var STORAGE_KEY = 'theme';
    var root = document.documentElement;
    var media = window.matchMedia('(prefers-color-scheme: dark)');

    function systemTheme() {
        return media.matches ? 'dark' : 'light';
    }

    function getStoredTheme() {
        return localStorage.getItem(STORAGE_KEY);
    }

    function currentTheme() {
        return root.getAttribute('data-theme') || systemTheme();
    }

    function applyTheme(theme) {
        root.setAttribute('data-theme', theme);
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.textContent = theme === 'dark' ? 'Dark Mode' : 'Light Mode';
        });
        document.dispatchEvent(new CustomEvent('themechange', { detail: { theme: theme } }));
    }

    // persist: false lets the OS-preference listener update the page
    // without overriding a theme the user picked manually.
    function setTheme(theme, persist) {
        if (persist !== false) {
            localStorage.setItem(STORAGE_KEY, theme);
        }
        applyTheme(theme);
    }

    function toggleTheme() {
        setTheme(currentTheme() === 'dark' ? 'light' : 'dark');
    }

    // Follow the OS setting live, but only while the user hasn't chosen a theme explicitly.
    media.addEventListener('change', function (e) {
        if (!getStoredTheme()) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    document.addEventListener('DOMContentLoaded', function () {
        applyTheme(currentTheme());
        document.querySelectorAll('.theme-toggle').forEach(function (btn) {
            btn.addEventListener('click', toggleTheme);
        });
    });

    window.DoombladeTheme = { get: currentTheme, set: setTheme, toggle: toggleTheme };
})();
