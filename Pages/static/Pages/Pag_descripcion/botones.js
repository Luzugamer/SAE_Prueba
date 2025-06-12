/**
 * Archivo: auth-buttons.js
 * Descripción: Manejo de animaciones y eventos para los botones de autenticación
 * Colores utilizados: d8fbf4, 241047, 43e2a3, 88a4ac, 15e58b, 8df7da, fefffe, 0ef26c, 17d347, a484b6
 */

document.addEventListener('DOMContentLoaded', function() {
    // Elementos del DOM
    const authContainer = document.getElementById('authButtonsContainer');
    const registerBtn = document.getElementById('registerBtn');
    const loginBtn = document.getElementById('loginBtn');
    
    // Configuración de colores
    const colors = {
        primary: '#17d347',      // Verde primario
        secondary: '#15e58b',    // Verde secundario
        accent: '#43e2a3',       // Verde acento
        light: '#d8fbf4',        // Verde claro
        dark: '#241047',         // Morado oscuro
        neutral: '#88a4ac',      // Gris azulado
        bright: '#0ef26c',       // Verde brillante
        aqua: '#8df7da',         // Aqua
        white: '#fefffe',        // Blanco
        purple: '#a484b6'        // Púrpura
    };

    // Función para crear efecto de partículas
    function createParticleEffect(button) {
        const rect = button.getBoundingClientRect();
        const particleCount = 8;
        
        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'auth-particle';
            particle.style.cssText = `
                position: fixed;
                width: 4px;
                height: 4px;
                background: ${Math.random() > 0.5 ? colors.primary : colors.bright};
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                left: ${rect.left + rect.width / 2}px;
                top: ${rect.top + rect.height / 2}px;
                opacity: 1;
                transform: scale(1);
                transition: all 0.6s ease-out;
            `;
            
            document.body.appendChild(particle);
            
            // Animar partícula
            setTimeout(() => {
                const angle = (i / particleCount) * Math.PI * 2;
                const distance = 50;
                particle.style.transform = `
                    translate(${Math.cos(angle) * distance}px, ${Math.sin(angle) * distance}px) 
                    scale(0)
                `;
                particle.style.opacity = '0';
            }, 10);
            
            // Eliminar partícula
            setTimeout(() => {
                particle.remove();
            }, 600);
        }
    }

    // Función para crear ondas de color
    function createColorWave(button, color) {
        const wave = document.createElement('div');
        wave.className = 'color-wave';
        wave.style.cssText = `
            position: absolute;
            top: 50%;
            left: 50%;
            width: 20px;
            height: 20px;
            background: radial-gradient(circle, ${color}40, transparent);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            pointer-events: none;
            animation: waveExpand 0.6s ease-out forwards;
        `;
        
        button.appendChild(wave);
        
        setTimeout(() => {
            wave.remove();
        }, 600);
    }

    // Función para animación de entrada dinámica
    function animateButtonEntrance() {
        if (!authContainer) return;
        
        // Resetear posición inicial
        authContainer.style.opacity = '0';
        authContainer.style.transform = 'translateY(-50px) scale(0.8)';
        
        // Aplicar animación con delay
        setTimeout(() => {
            authContainer.style.transition = 'all 1s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            authContainer.style.opacity = '1';
            authContainer.style.transform = 'translateY(0) scale(1)';
        }, 800);
        
        // Animar botones individualmente
        if (registerBtn) {
            setTimeout(() => {
                registerBtn.style.animation = 'bounceInRight 0.8s ease-out forwards';
            }, 1000);
        }
        
        if (loginBtn) {
            setTimeout(() => {
                loginBtn.style.animation = 'bounceInLeft 0.8s ease-out forwards';
            }, 1200);
        }
    }

    // Event listeners para los botones
    if (registerBtn) {
        registerBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Efecto visual
            createParticleEffect(this);
            createColorWave(this, colors.primary);
            
            // Añadir clase de animación
            this.classList.add('clicked');
            setTimeout(() => this.classList.remove('clicked'), 300);
        });
        
        // Efecto hover mejorado
        registerBtn.addEventListener('mouseenter', function() {
            this.style.background = `linear-gradient(135deg, ${colors.bright}, ${colors.primary}, ${colors.secondary})`;
            this.style.boxShadow = `0 8px 25px ${colors.primary}60`;
        });
        
        registerBtn.addEventListener('mouseleave', function() {
            this.style.background = `linear-gradient(135deg, ${colors.primary}, ${colors.secondary}, ${colors.bright})`;
            this.style.boxShadow = `0 4px 15px rgba(0, 0, 0, 0.1)`;
        });
    }

    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Efecto visual
            createParticleEffect(this);
            createColorWave(this, colors.accent);
            
            // Añadir clase de animación
            this.classList.add('clicked');
            setTimeout(() => this.classList.remove('clicked'), 300);
        });
        
        // Efecto hover mejorado
        loginBtn.addEventListener('mouseenter', function() {
            this.style.background = `linear-gradient(135deg, ${colors.accent}, ${colors.aqua}, ${colors.light})`;
            this.style.boxShadow = `0 8px 25px ${colors.accent}60`;
        });
        
        loginBtn.addEventListener('mouseleave', function() {
            this.style.background = `linear-gradient(135deg, ${colors.aqua}, ${colors.light}, ${colors.accent})`;
            this.style.boxShadow = `0 4px 15px rgba(0, 0, 0, 0.1)`;
        });
    }

    // Función para crear efecto de typing en el texto
    function typeText(element, text, speed = 50) {
        if (!element) return;
        
        element.textContent = '';
        let i = 0;
        
        const timer = setInterval(() => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                i++;
            } else {
                clearInterval(timer);
            }
        }, speed);
    }

    // Efecto de respiración para los botones
    function breathingEffect() {
        const buttons = [registerBtn, loginBtn];
        buttons.forEach((button, index) => {
            if (button) {
                setInterval(() => {
                    button.style.transform = 'scale(1.02)';
                    setTimeout(() => {
                        button.style.transform = 'scale(1)';
                    }, 1000);
                }, 4000 + (index * 500));
            }
        });
    }

    // Inicializar animaciones
    animateButtonEntrance();
    
    // Iniciar efecto de respiración después de la animación inicial
    setTimeout(breathingEffect, 2000);

    const dynamicStyles = `
    @keyframes waveExpand {
        0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 0.6;
        }
        100% {
            transform: translate(-50%, -50%) scale(8);
            opacity: 0;
        }
    }

    @keyframes bounceInRight {
        0% {
            opacity: 0;
            transform: translateX(200px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes bounceInLeft {
        0% {
            opacity: 0;
            transform: translateX(-200px);
        }
        100% {
            opacity: 1;
            transform: translateX(0);
        }
    }
    `;

    const styleSheet = document.createElement('style');
    styleSheet.textContent = dynamicStyles;
    document.head.appendChild(styleSheet);


    // Función para manejar scroll y mostrar/ocultar botones
    let lastScrollY = window.scrollY;
    let ticking = false;

    function updateButtonsOnScroll() {
        const scrollY = window.scrollY;
        
        if (authContainer) {
            if (scrollY > lastScrollY && scrollY > 100) {
                // Scrolling down - hide buttons
                authContainer.style.transform = 'translateY(-100px)';
                authContainer.style.opacity = '0.7';
            } else {
                // Scrolling up - show buttons
                authContainer.style.transform = 'translateY(0)';
                authContainer.style.opacity = '1';
            }
        }
        
        lastScrollY = scrollY;
        ticking = false;
    }

    function requestTick() {
        if (!ticking) {
            requestAnimationFrame(updateButtonsOnScroll);
            ticking = true;
        }
    }

    // Event listener para scroll
    window.addEventListener('scroll', requestTick);
});

// Funciones globales para uso externo
window.AuthButtons = {
    
    // Función para ocultar/mostrar botones
    toggle: function(show = true) {
        const container = document.getElementById('authButtonsContainer');
        if (container) {
            container.style.display = show ? 'block' : 'none';
        }
    },
    
    // Función para cambiar texto de botones
    setText: function(registerText, loginText) {
        const registerBtn = document.querySelector('#registerBtn .btn-text');
        const loginBtn = document.querySelector('#loginBtn .btn-text');
        
        if (registerBtn && registerText) registerBtn.textContent = registerText;
        if (loginBtn && loginText) loginBtn.textContent = loginText;
    }
};