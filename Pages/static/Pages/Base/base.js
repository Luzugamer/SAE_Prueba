document.addEventListener('DOMContentLoaded', function () {
    const bottomNavbar = document.getElementById('bottomNavbar');
    const navItems = document.querySelectorAll('.nav-item');

    // Solo efectos visuales para los nav items
    navItems.forEach(item => {
        item.addEventListener('click', function (e) {
            // NO preventDefault() - permite que los enlaces funcionen normalmente
            
            // Remover clase active de todos los items
            navItems.forEach(nav => nav.classList.remove('active'));
            
            // Agregar clase active al item clickeado
            this.classList.add('active');
        });

        item.addEventListener('mouseleave', function() {
            if (!this.classList.contains('active')) {
                this.style.transform = '';
            }
        });
    });

    // Funcionalidad de hover para mostrar/ocultar navbar
    if (bottomNavbar) {
        let hoverTimeout;

        // Evento para mostrar navbar al hacer hover
        bottomNavbar.addEventListener('mouseenter', function() {
            clearTimeout(hoverTimeout);
            this.style.transform = 'translateX(-50%) translateY(0)';
        });

        // Evento para ocultar navbar al quitar el mouse
        bottomNavbar.addEventListener('mouseleave', function() {
            hoverTimeout = setTimeout(() => {
                this.style.transform = 'translateX(-50%) translateY(85%)';
            }, 300); // Pequeño delay para evitar parpadeo
        });

        // Mantener visible si el usuario está interactuando con los elementos
        navItems.forEach(item => {
            item.addEventListener('mouseenter', function() {
                clearTimeout(hoverTimeout);
            });
        });
    }

    // Mejorar la experiencia táctil en dispositivos móviles
    if ('ontouchstart' in window) {
        navItems.forEach(item => {
            item.addEventListener('touchstart', function() {
                this.style.transform = 'translateY(-5px) scale(1.02)';
            });

            item.addEventListener('touchend', function() {
                setTimeout(() => {
                    if (!this.classList.contains('active')) {
                        this.style.transform = '';
                    }
                }, 150);
            });
        });

        // Funcionalidad táctil para dispositivos móviles
        if (bottomNavbar) {
            let touchStartY = 0;
            let isNavbarVisible = false;

            bottomNavbar.addEventListener('touchstart', function(e) {
                touchStartY = e.touches[0].clientY;
            });

            bottomNavbar.addEventListener('touchend', function(e) {
                const touchEndY = e.changedTouches[0].clientY;
                const touchDiff = touchStartY - touchEndY;

                // Si el usuario hace swipe hacia arriba, mostrar navbar
                if (touchDiff > 30 && !isNavbarVisible) {
                    this.style.transform = 'translateX(-50%) translateY(0)';
                    isNavbarVisible = true;
                    
                    // Auto-ocultar después de 3 segundos sin interacción
                    setTimeout(() => {
                        if (isNavbarVisible) {
                            this.style.transform = 'translateX(-50%) translateY(85%)';
                            isNavbarVisible = false;
                        }
                    }, 3000);
                }
                // Si el usuario hace swipe hacia abajo, ocultar navbar
                else if (touchDiff < -30 && isNavbarVisible) {
                    this.style.transform = 'translateX(-50%) translateY(85%)';
                    isNavbarVisible = false;
                }
            });
        }
    }

    // Funcionalidad adicional: mostrar navbar temporalmente cuando se carga la página
    if (bottomNavbar) {
        // Mostrar completamente por 2 segundos al cargar la página
        setTimeout(() => {
            bottomNavbar.style.transform = 'translateX(-50%) translateY(0)';
        }, 500);

        // Luego ocultar automáticamente
        setTimeout(() => {
            bottomNavbar.style.transform = 'translateX(-50%) translateY(85%)';
        }, 2500);
    }
});