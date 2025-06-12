// Efecto parallax y animaciones en scroll
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;
    
    // Efecto parallax en el fondo
    const parallaxBg = document.querySelector('.parallax-bg');
    if (parallaxBg) {
        parallaxBg.style.transform = `translateY(${rate}px)`;
    }
    
    // Fade del hero content basado en scroll
    const heroContent = document.querySelector('.hero-content');
    const heroSection = document.querySelector('.hero-section');
    const heroHeight = heroSection.offsetHeight;
    
    if (scrolled < heroHeight) {
        const opacity = 1 - (scrolled / heroHeight) * 1.5;
        const transform = scrolled * 0.5;
        heroContent.style.opacity = Math.max(0, opacity);
        heroContent.style.transform = `translateY(${transform}px)`;
    }
});

// Animaciones de entrada para las tarjetas principales
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const card = entry.target;
            const row = card.getAttribute('data-row');
            
            if (row) {
                // Animación para cards principales
                const baseDelay = row === '1' ? 0 : 400;
                const cardIndex = Array.from(card.parentElement.children).indexOf(card);
                const cardDelay = cardIndex * 100;
                
                setTimeout(() => {
                    card.classList.add('slide-in-right');
                }, baseDelay + cardDelay);
            } else {
                // Animación para otros elementos
                entry.target.classList.add('visible');
            }
            
            observer.unobserve(card);
        }
    });
}, observerOptions);

// Observar elementos para animaciones
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.content-card');
    const fadeElements = document.querySelectorAll('.fade-in-up');
    
    [...cards, ...fadeElements].forEach((element, index) => {
        if (element.classList.contains('fade-in-up')) {
            element.style.transitionDelay = `${index * 0.01}s`;
        }
        observer.observe(element);
    });
});

// Smooth scroll
document.documentElement.style.scrollBehavior = 'smooth';

// Efecto de entrada inicial
window.addEventListener('load', () => {
    document.querySelector('.hero-content').style.opacity = '1';
    document.querySelector('.hero-content').style.transform = 'translateY(0)';
});