(function () {
    'use strict';

    document.addEventListener('DOMContentLoaded', function () {
        var app = document.querySelector('.app');
        var sidebar = document.querySelector('.sidebar');
        var toggle = document.querySelector('[data-sidebar-toggle]');
        var scrim = document.querySelector('[data-sidebar-scrim]');

        function setSidebar(open) {
            if (!app) return;
            app.classList.toggle('sidebar-open', open);
            if (toggle) toggle.setAttribute('aria-expanded', String(open));
            document.body.classList.toggle('no-scroll', open && window.innerWidth < 1024);
        }

        if (toggle) {
            toggle.addEventListener('click', function () {
                setSidebar(!app.classList.contains('sidebar-open'));
            });
        }

        if (scrim) {
            scrim.addEventListener('click', function () { setSidebar(false); });
        }

        if (sidebar) {
            sidebar.querySelectorAll('.nav-link').forEach(function (link) {
                link.addEventListener('click', function () {
                    if (window.innerWidth < 1024) setSidebar(false);
                });
            });
        }

        window.addEventListener('resize', function () {
            if (window.innerWidth >= 1024) {
                document.body.classList.remove('no-scroll');
            }
        });

        document.querySelectorAll('.alert[data-dismiss]').forEach(function (alert) {
            setTimeout(function () {
                alert.style.transition = 'opacity .4s ease, transform .4s ease';
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-6px)';
                setTimeout(function () { alert.remove(); }, 400);
            }, 4200);
        });

        document.querySelectorAll('[data-confirm]').forEach(function (el) {
            el.addEventListener('click', function (event) {
                if (!window.confirm(el.getAttribute('data-confirm'))) {
                    event.preventDefault();
                }
            });
        });
    });
})();
