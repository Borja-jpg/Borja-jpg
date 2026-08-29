/* ============================================
   NEXARA MADRID — JavaScript Principal
   ============================================
   VÍDEOS: Cuando tengas la carpeta VIDEOSRECURSO lista,
   copia los vídeos a assets/videos/ con nombres video1.mp4,
   video2.mp4, video3.mp4 — o sustituye los placeholders del
   HTML por iframes de YouTube con tus IDs reales.
   ============================================ */

// ---- Navbar scroll effect ----
const navbar = document.getElementById('navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar.classList.add('scrolled');
  } else {
    navbar.classList.remove('scrolled');
  }
});

// ---- Hamburger menu ----
const hamburger = document.getElementById('hamburger');
const navLinks = document.getElementById('navLinks');

hamburger.addEventListener('click', () => {
  navLinks.classList.toggle('open');
  const spans = hamburger.querySelectorAll('span');
  spans[0].style.transform = navLinks.classList.contains('open') ? 'rotate(45deg) translate(5px, 5px)' : '';
  spans[1].style.opacity = navLinks.classList.contains('open') ? '0' : '1';
  spans[2].style.transform = navLinks.classList.contains('open') ? 'rotate(-45deg) translate(5px, -5px)' : '';
});

// Cerrar menú al hacer click en un enlace
navLinks.querySelectorAll('a').forEach(link => {
  link.addEventListener('click', () => {
    navLinks.classList.remove('open');
    hamburger.querySelectorAll('span').forEach(s => { s.style.transform = ''; s.style.opacity = '1'; });
  });
});

// ---- Precio tabs ----
const priceTabs = document.querySelectorAll('.price-tab');
const priceTables = document.querySelectorAll('.price-table');

priceTabs.forEach(tab => {
  tab.addEventListener('click', () => {
    const brand = tab.getAttribute('data-brand');
    priceTabs.forEach(t => t.classList.remove('active'));
    priceTables.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');
    document.getElementById(brand).classList.add('active');
  });
});

// ---- Formulario de contacto → WhatsApp ----
const contactForm = document.getElementById('contactForm');
if (contactForm) {
  contactForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const nombre = document.getElementById('nombre').value.trim();
    const telefono = document.getElementById('telefono').value.trim();
    const movil = document.getElementById('movil').value.trim();
    const averia = document.getElementById('averia').value.trim();

    const mensaje = encodeURIComponent(
      `Hola! Me llamo ${nombre}.\n` +
      `📱 Modelo: ${movil}\n` +
      `🔧 Avería: ${averia}\n` +
      `📞 Mi teléfono: ${telefono}`
    );

    // Reemplaza 34603164544 con tu número real
    window.open(`https://wa.me/34603164544?text=${mensaje}`, '_blank');
  });
}

// ---- Scroll reveal (animación suave al aparecer) ----
const observerOptions = {
  threshold: 0.1,
  rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = '1';
      entry.target.style.transform = 'translateY(0)';
      observer.unobserve(entry.target);
    }
  });
}, observerOptions);

// Aplica animación de entrada a cards
document.querySelectorAll('.step-card, .service-card, .video-card, .review-card, .garantia-item').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(30px)';
  el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
  observer.observe(el);
});

// ---- Smooth scroll para enlaces ancla ----
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function(e) {
    const target = document.querySelector(this.getAttribute('href'));
    if (target) {
      e.preventDefault();
      const offset = 80; // altura del navbar
      const top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({ top, behavior: 'smooth' });
    }
  });
});

// ---- Video placeholder click (muestra alert) ----
document.querySelectorAll('.video-placeholder').forEach(placeholder => {
  placeholder.addEventListener('click', () => {
    alert('¡Próximamente aquí encontrarás el vídeo real de la reparación!\n\nSíguenos en TikTok e Instagram @nexaramadrid para ver nuestros vídeos en directo.\n\nO escríbenos por WhatsApp y te los enviamos directamente.');
  });
});
