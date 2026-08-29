/* ============================================
   NEXARA MADRID — JavaScript 2.0
   Interactive Logic, Calculator & Animations
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {

  const PHONE_NUMBER = '34603164544';

  // ---- 1. Navbar Scroll Effect ----
  const navbar = document.getElementById('navbar');
  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }
  });

  // ---- 2. Mobile Hamburger Menu ----
  const hamburger = document.getElementById('hamburger');
  const navLinks = document.getElementById('navLinks');

  if (hamburger && navLinks) {
    hamburger.addEventListener('click', () => {
      navLinks.classList.toggle('open');
      const spans = hamburger.querySelectorAll('span');
      if (navLinks.classList.contains('open')) {
        spans[0].style.transform = 'rotate(45deg) translate(5px, 5px)';
        spans[1].style.opacity = '0';
        spans[2].style.transform = 'rotate(-45deg) translate(5px, -5px)';
      } else {
        spans[0].style.transform = '';
        spans[1].style.opacity = '1';
        spans[2].style.transform = '';
      }
    });

    navLinks.querySelectorAll('a').forEach(link => {
      link.addEventListener('click', () => {
        navLinks.classList.remove('open');
        const spans = hamburger.querySelectorAll('span');
        spans[0].style.transform = '';
        spans[1].style.opacity = '1';
        spans[2].style.transform = '';
      });
    });
  }

  // ---- 3. Interactive Price Calculator ----
  const brandButtons = document.querySelectorAll('.brand-btn');
  const issueButtons = document.querySelectorAll('.issue-btn');
  const calcZonaInput = document.getElementById('calcZona');
  const calcPriceDisplay = document.getElementById('calcPriceDisplay');
  const calcTimeDisplay = document.getElementById('calcTimeDisplay');
  const calcWhatsAppBtn = document.getElementById('calcWhatsAppBtn');

  // Base prices matrix for calculation [brand][issue]
  const priceMatrix = {
    iphone: {
      pantalla: { price: '69€', time: '25-30 min', label: 'Pantalla OLED/Retina iPhone' },
      bateria: { price: '59€', time: '15-20 min', label: 'Batería iPhone Alta Capacidad' },
      conector: { price: '55€', time: '20-25 min', label: 'Puerto Lightning/USB-C iPhone' },
      tapa: { price: '59€', time: '35-45 min', label: 'Cristal Trasero iPhone' }
    },
    samsung: {
      pantalla: { price: '59€', time: '25-35 min', label: 'Pantalla AMOLED Samsung Galaxy' },
      bateria: { price: '45€', time: '15-20 min', label: 'Batería Samsung Galaxy' },
      conector: { price: '50€', time: '20-25 min', label: 'Conector de Carga USB-C Samsung' },
      tapa: { price: '49€', time: '30-40 min', label: 'Tapa Trasera Samsung Galaxy' }
    },
    xiaomi: {
      pantalla: { price: '49€', time: '20-30 min', label: 'Pantalla Xiaomi / Redmi / POCO' },
      bateria: { price: '39€', time: '15-20 min', label: 'Batería Xiaomi / Redmi' },
      conector: { price: '45€', time: '20-25 min', label: 'Puerto de Carga Xiaomi' },
      tapa: { price: '45€', time: '25-35 min', label: 'Tapa Trasera Xiaomi' }
    },
    otros: {
      pantalla: { price: '55€', time: '25-35 min', label: 'Pantalla Multimarca (Pixel, Huawei, OPPO)' },
      bateria: { price: '39€', time: '15-25 min', label: 'Batería Multimarca' },
      conector: { price: '45€', time: '20-25 min', label: 'Puerto de Carga' },
      tapa: { price: '45€', time: '30-40 min', label: 'Tapa Trasera' }
    }
  };

  let selectedBrand = 'iphone';
  let selectedIssue = 'pantalla';

  function updateCalculator() {
    const data = priceMatrix[selectedBrand][selectedIssue];
    if (data && calcPriceDisplay && calcTimeDisplay) {
      calcPriceDisplay.textContent = data.price;
      calcTimeDisplay.innerHTML = `<i class="fas fa-clock"></i> ${data.time}`;
      
      const zona = calcZonaInput ? (calcZonaInput.value.trim() || 'Madrid') : 'Madrid';
      const brandName = selectedBrand.toUpperCase();
      
      const message = encodeURIComponent(
        `¡Hola! He calculado el presupuesto en vuestra web:\n` +
        `📱 Dispositivo: ${brandName}\n` +
        `🔧 Reparación: ${data.label} (${data.price})\n` +
        `⏱ Tiempo estimado: ${data.time}\n` +
        `📍 Mi zona en Madrid: ${zona}\n\n` +
        `¿Tienes disponibilidad para venir con el coche taller hoy?`
      );

      if (calcWhatsAppBtn) {
        calcWhatsAppBtn.href = `https://wa.me/${PHONE_NUMBER}?text=${message}`;
      }
    }
  }

  brandButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      brandButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedBrand = btn.getAttribute('data-brand');
      updateCalculator();
    });
  });

  issueButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      issueButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedIssue = btn.getAttribute('data-issue');
      updateCalculator();
    });
  });

  if (calcZonaInput) {
    calcZonaInput.addEventListener('input', updateCalculator);
  }

  updateCalculator();

  // ---- 4. Price Tabs Switcher ----
  const priceTabs = document.querySelectorAll('.price-tab');
  const priceTables = document.querySelectorAll('.price-table');

  priceTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      const brand = tab.getAttribute('data-brand');
      priceTabs.forEach(t => t.classList.remove('active'));
      priceTables.forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      const targetTable = document.getElementById(brand);
      if (targetTable) {
        targetTable.classList.add('active');
      }
    });
  });

  // ---- 5. FAQ Accordion ----
  const faqItems = document.querySelectorAll('.faq-item');

  faqItems.forEach(item => {
    const questionBtn = item.querySelector('.faq-question');
    if (questionBtn) {
      questionBtn.addEventListener('click', () => {
        const isActive = item.classList.contains('active');
        // Close others
        faqItems.forEach(other => other.classList.remove('active'));
        if (!isActive) {
          item.classList.add('active');
        }
      });
    }
  });

  // Open the first FAQ item by default
  if (faqItems.length > 0) {
    faqItems[0].classList.add('active');
  }

  // ---- 6. Contact Form -> WhatsApp ----
  const contactForm = document.getElementById('contactForm');
  if (contactForm) {
    contactForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const nombre = document.getElementById('nombre').value.trim();
      const telefono = document.getElementById('telefono').value.trim();
      const movil = document.getElementById('movil').value.trim();
      const averia = document.getElementById('averia').value.trim();

      const mensaje = encodeURIComponent(
        `¡Hola NEXARA! Solicito presupuesto express:\n` +
        `👤 Nombre: ${nombre}\n` +
        `📞 Teléfono: ${telefono}\n` +
        `📱 Móvil / Modelo: ${movil}\n` +
        `🔧 Avería y ubicación: ${averia}\n\n` +
        `¿Cuándo podrías desplazarte con el coche taller?`
      );

      window.open(`https://wa.me/${PHONE_NUMBER}?text=${mensaje}`, '_blank');
    });
  }

  // ---- 7. WhatsApp Toast Notification ----
  const waToast = document.getElementById('waToast');
  const toastClose = document.getElementById('toastClose');

  if (waToast) {
    setTimeout(() => {
      waToast.classList.add('show');
    }, 3500);

    if (toastClose) {
      toastClose.addEventListener('click', (e) => {
        e.stopPropagation();
        waToast.classList.remove('show');
      });
    }
  }

  // ---- 8. Smooth Scroll for Anchor Links ----
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      const href = this.getAttribute('href');
      if (href !== '#' && href.length > 1) {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          const offset = 80;
          const top = target.getBoundingClientRect().top + window.scrollY - offset;
          window.scrollTo({ top, behavior: 'smooth' });
        }
      }
    });
  });

  // ---- 9. Scroll Reveal Fade-in Animations ----
  const revealElements = document.querySelectorAll(
    '.step-card, .service-card, .video-card, .review-card, .garantia-item, .vs-card, .calculator-card'
  );

  const revealObserver = new IntersectionObserver((entries, observer) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, {
    threshold: 0.08,
    rootMargin: '0px 0px -40px 0px'
  });

  revealElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(24px)';
    el.style.transition = 'opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), transform 0.6s cubic-bezier(0.16, 1, 0.3, 1)';
    revealObserver.observe(el);
  });

});
