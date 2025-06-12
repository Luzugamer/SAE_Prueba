document.addEventListener('DOMContentLoaded', function() {
    const cardsContainer = document.getElementById('cardsContainer');
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const cards = document.querySelectorAll('.card');
    
    let currentIndex = 0;
    const totalCards = cards.length;
    const radius = 400;
    let isAnimating = false; // Flag para controlar que termine la animación
    
    // Calcular el ángulo entre cada carta
    const angleStep = 360 / totalCards;
    
    function updateCarousel() {
        // Marcar que está animando
        isAnimating = true;
        
        // Rotar el contenedor principal
        const rotation = -currentIndex * angleStep;
        console.log('updateCarousel - rotation:', rotation, 'degrees');
        cardsContainer.style.transform = `rotateY(${rotation}deg)`;
        console.log('Applied transform:', cardsContainer.style.transform);
        
        // Actualizar clases de las cartas para efectos visuales
        cards.forEach((card, index) => {
            card.classList.remove('active', 'side', 'back');
            
            // Calcular la posición relativa de cada carta
            let relativeIndex = (index - currentIndex + totalCards) % totalCards;
            
            if (relativeIndex === 0) {
                card.classList.add('active');
            } else if (relativeIndex === 1 || relativeIndex === totalCards - 1) {
                card.classList.add('side');
            } else {
                card.classList.add('back');
            }
        });
        
        // Esperar a que termine la animación CSS (300ms + margen de seguridad)
        setTimeout(() => {
            isAnimating = false;
            console.log('Animation completed, ready for next transition');
        }, 350);
    }
    
    function updateNavigationButtons() {
        // Los botones siempre están habilitados en un carrusel continuo
        prevBtn.classList.remove('disabled');
        nextBtn.classList.remove('disabled');
    }
    
    function nextCard() {
        // No permitir nueva transición hasta que termine la animación actual
        if (isAnimating) {
            console.log('Animation in progress, ignoring click');
            return;
        }
        
        console.log('nextCard called - currentIndex before:', currentIndex);
        
        // Avanzar al siguiente índice
        currentIndex = (currentIndex + 1) % totalCards;
        
        // Si llegamos al final, continuar desde el inicio (comportamiento de cinta)
        if (currentIndex === 0) {
            console.log('Reached end, continuing from beginning');
        }
        
        console.log('nextCard called - currentIndex after:', currentIndex);
        updateCarousel();
    }
    
    function prevCard() {
        // No permitir nueva transición hasta que termine la animación actual
        if (isAnimating) {
            console.log('Animation in progress, ignoring click');
            return;
        }
        
        console.log('prevCard called - currentIndex before:', currentIndex);
        
        // Retroceder al índice anterior
        currentIndex = (currentIndex - 1 + totalCards) % totalCards;
        
        // Si llegamos al inicio yendo hacia atrás, continuar desde el final
        if (currentIndex === totalCards - 1) {
            console.log('Reached beginning, continuing from end');
        }
        
        console.log('prevCard called - currentIndex after:', currentIndex);
        updateCarousel();
    }
    
    // Posicionar las cartas en círculo con mayor radio
    function positionCards() {
        cards.forEach((card, index) => {
            const angle = index * angleStep;
            
            // Posicionar cada carta en el círculo
            card.style.transform = `rotateY(${angle}deg) translateZ(${radius}px)`;
        });
    }
    
    // Función para animar el hover de los iconos
    function animateIconHover(icon, scale = 1.1) {
        icon.style.transform = `scale(${scale})`;
    }
    
    // Función para la animación flotante
    function startFloatingAnimation(element) {
        element.style.animation = 'float 3s ease-in-out infinite';
    }
    
    function stopFloatingAnimation(element) {
        element.style.animation = 'none';
    }
    
    // Event listeners para navegación
    nextBtn.addEventListener('click', function() {
        console.log('Right button clicked!');
        nextCard();
        
        // Actualizar animación activa después de que termine la transición
        setTimeout(() => {
            if (!isAnimating) {
                updateActiveCardAnimation();
            }
        }, 350);
    });
    
    prevBtn.addEventListener('click', function() {
        console.log('Left button clicked!');
        prevCard();
        
        // Actualizar animación activa después de que termine la transición
        setTimeout(() => {
            if (!isAnimating) {
                updateActiveCardAnimation();
            }
        }, 350);
    });
    
    // Click en las cartas para navegar
    cards.forEach((card, index) => {
        card.addEventListener('click', function() {
            if (index !== currentIndex && !isAnimating) {
                currentIndex = index;
                updateCarousel();
                
                // Actualizar animación activa después de que termine la transición
                setTimeout(() => {
                    if (!isAnimating) {
                        updateActiveCardAnimation();
                    }
                }, 350);
            }
        });
        
        // Animaciones de hover para cada carta
        card.addEventListener('mouseenter', function() {
            const icon = card.querySelector('.icon');
            if (card.classList.contains('active')) {
                animateIconHover(icon, 1.2);
                startFloatingAnimation(icon);
            } else {
                animateIconHover(icon, 1.05);
            }
        });
        
        card.addEventListener('mouseleave', function() {
            const icon = card.querySelector('.icon');
            animateIconHover(icon, 1);
            if (!card.classList.contains('active')) {
                stopFloatingAnimation(icon);
            }
        });
    });
    
    // Animación especial para la carta activa
    function updateActiveCardAnimation() {
        cards.forEach(card => {
            const icon = card.querySelector('.icon');
            if (card.classList.contains('active')) {
                startFloatingAnimation(icon);
            } else {
                stopFloatingAnimation(icon);
            }
        });
    }
    
    // Navegación con teclado
    document.addEventListener('keydown', function(e) {
        if (e.key === 'ArrowLeft') {
            prevCard();
        } else if (e.key === 'ArrowRight') {
            nextCard();
        }
    });
    
    // Inicializar el carrusel
    positionCards();
    updateCarousel();
    
    // Esperar a que termine la inicialización para activar animaciones
    setTimeout(() => {
        updateActiveCardAnimation();
    }, 350);
    
    // Soporte para touch/swipe en dispositivos móviles
    let startX = 0;
    let startY = 0;
    let distX = 0;
    let distY = 0;
    let isSwipping = false;
    
    cardsContainer.addEventListener('touchstart', function(e) {
        if (!isAnimating) {
            const touch = e.touches[0];
            startX = touch.clientX;
            startY = touch.clientY;
            isSwipping = true;
        }
    });
    
    cardsContainer.addEventListener('touchmove', function(e) {
        if (isSwipping && !isAnimating) {
            e.preventDefault(); // Prevenir scroll
        }
    });
    
    cardsContainer.addEventListener('touchend', function(e) {
        if (!isSwipping || isAnimating) return;
        
        const touch = e.changedTouches[0];
        distX = touch.clientX - startX;
        distY = touch.clientY - startY;
        
        // Solo si el swipe es más horizontal que vertical
        if (Math.abs(distX) > Math.abs(distY) && Math.abs(distX) > 50) {
            if (distX > 0) {
                prevCard(); // Swipe derecha = anterior
            } else {
                nextCard(); // Swipe izquierda = siguiente
            }
        }
        
        isSwipping = false;
    });
    
    // Animaciones para los botones de navegación
    function animateButton(button, scale = 1.15) {
        button.style.transform = `scale(${scale}) translateY(-50%)`;
    }
    
    // Event listeners para animaciones de botones
    [prevBtn, nextBtn].forEach(button => {
        button.addEventListener('mouseenter', function() {
            if (!isAnimating) {
                animateButton(this, 1.15);
            }
        });
        
        button.addEventListener('mouseleave', function() {
            animateButton(this, 1);
        });
        
        button.addEventListener('mousedown', function() {
            if (!isAnimating) {
                animateButton(this, 1.05);
            }
        });
        
        button.addEventListener('mouseup', function() {
            if (!isAnimating) {
                animateButton(this, 1.15);
            }
        });
    });
    
    // Feedback visual para cuando se intenta navegar durante animación
    function showAnimationFeedback(button) {
        button.style.opacity = '0.5';
        setTimeout(() => {
            button.style.opacity = '1';
        }, 100);
    }
    
    // Agregar feedback visual a los botones cuando no se puede navegar
    [prevBtn, nextBtn].forEach(button => {
        const originalClick = button.onclick;
        button.addEventListener('click', function(e) {
            if (isAnimating) {
                showAnimationFeedback(this);
                e.stopPropagation();
            }
        });
    });
});