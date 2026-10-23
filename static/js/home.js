(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var nav = document.getElementById('siteNav');
        var toggle = document.querySelector('[data-nav-toggle]');
        var toggleIcon = toggle ? toggle.querySelector('i') : null;

        if (toggle && nav) {
            toggle.addEventListener('click', function () {
                var open = nav.classList.toggle('menu-open');
                toggle.setAttribute('aria-expanded', String(open));
                if (toggleIcon) {
                    toggleIcon.className = open ? 'fa-solid fa-xmark' : 'fa-solid fa-bars';
                }
            });

            nav.querySelectorAll('.nav-links a').forEach(function (link) {
                link.addEventListener('click', function () {
                    nav.classList.remove('menu-open');
                    toggle.setAttribute('aria-expanded', 'false');
                    if (toggleIcon) toggleIcon.className = 'fa-solid fa-bars';
                });
            });
        }

        function onScroll() {
            if (!nav) return;
            nav.classList.toggle('scrolled', window.scrollY > 12);
        }

        onScroll();
        window.addEventListener('scroll', onScroll, { passive: true });

        var reveals = document.querySelectorAll('.reveal');

        if ('IntersectionObserver' in window) {
            var observer = new IntersectionObserver(function (entries) {
                entries.forEach(function (entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('is-visible');
                        observer.unobserve(entry.target);
                    }
                });
            }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

            reveals.forEach(function (el) { observer.observe(el); });
        } else {
            reveals.forEach(function (el) { el.classList.add('is-visible'); });
        }
    });
})();
