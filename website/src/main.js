import './style.css'
import { setupI18n } from './i18n.js'

setupI18n();

// Adiciona rolagem suave para links de âncora.
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', function (e) {
    e.preventDefault();
    const targetId = this.getAttribute('href');
    if (targetId === '#') return;

    const targetElement = document.querySelector(targetId);
    if (targetElement) {
      targetElement.scrollIntoView({
        behavior: 'smooth',
        block: 'start'
      });
    }
  });
});

// Adiciona um efeito simples de navbar ao rolar a página.
const navbar = document.querySelector('.navbar');
window.addEventListener('scroll', () => {
  if (window.scrollY > 50) {
    navbar.style.boxShadow = '0 4px 30px rgba(0, 0, 0, 0.5)';
  } else {
    navbar.style.boxShadow = 'none';
  }
});

// Controle do modal de download.
const downloadBtn = document.getElementById('download-btn');
const downloadModal = document.getElementById('download-modal');
const closeModal = document.getElementById('close-modal');

if (downloadBtn && downloadModal) {
  downloadBtn.addEventListener('click', () => {
    downloadModal.classList.add('active');
    document.body.style.overflow = 'hidden';
  });

  const closeHandler = () => {
    downloadModal.classList.remove('active');
    document.body.style.overflow = '';
  };

  closeModal?.addEventListener('click', closeHandler);

  window.addEventListener('click', (e) => {
    if (e.target === downloadModal) {
      closeHandler();
    }
  });
}
