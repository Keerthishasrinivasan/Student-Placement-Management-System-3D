/**
 * Student Placement Management System - Main Interface Scripts
 */

document.addEventListener('DOMContentLoaded', () => {
  // 1. Auto-dismiss flash alerts after 5 seconds
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });

  // 2. Mobile Menu Toggle
  const menuToggle = document.getElementById('mobile-menu-toggle');
  const navLinks = document.getElementById('main-nav-links');
  if (menuToggle && navLinks) {
    menuToggle.addEventListener('click', () => {
      navLinks.classList.toggle('nav-links-mobile-open');
    });
  }

  // 3. Simple Modal Helpers
  window.openModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'flex';
  };

  window.closeModal = function(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.style.display = 'none';
  };
});
