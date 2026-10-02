'use strict';

// ── SCROLL PROGRESS ──
function initScrollProgress() {
  const bar = document.getElementById('scroll-progress');
  if (!bar) return;
  window.addEventListener('scroll', () => {
    const pct = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  }, { passive: true });
}

// ── NAVBAR ──
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  if (!navbar) return;
  window.addEventListener('scroll', () => {
    navbar.classList.toggle('scrolled', window.scrollY > 20);
  }, { passive: true });

  const hamburger = document.querySelector('.nav-hamburger');
  const mobileNav = document.querySelector('.nav-mobile');
  if (hamburger && mobileNav) {
    hamburger.addEventListener('click', () => {
      hamburger.classList.toggle('open');
      mobileNav.classList.toggle('open');
    });
  }
  document.querySelectorAll('.nav-mobile a').forEach(a => {
    a.addEventListener('click', () => {
      hamburger?.classList.remove('open');
      mobileNav?.classList.remove('open');
    });
  });
}

// ── NOTIFICATIONS ──
function initNotifications() {
  const btn      = document.getElementById('notif-btn');
  const dropdown = document.getElementById('notif-dropdown');
  if (!btn || !dropdown) return;

  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
    document.getElementById('profile-dropdown')?.classList.remove('open');
    if (dropdown.classList.contains('open')) loadNotifications();
  });
  document.addEventListener('click', () => dropdown.classList.remove('open'));
  dropdown.addEventListener('click', e => e.stopPropagation());

  document.getElementById('mark-all-read')?.addEventListener('click', async () => {
    await fetch('/api/notifications/read', { method: 'POST' });
    document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
    const badge = document.querySelector('.notif-badge');
    if (badge) badge.style.display = 'none';
  });
}

async function loadNotifications() {
  const list = document.getElementById('notif-list');
  if (!list) return;
  try {
    const res    = await fetch('/api/notifications');
    const notifs = await res.json();
    const badge  = document.querySelector('.notif-badge');
    const unread = notifs.filter(n => !n.is_read).length;
    if (badge) {
      badge.textContent    = unread || '';
      badge.style.display  = unread > 0 ? 'flex' : 'none';
    }
    list.innerHTML = notifs.length
      ? notifs.map(n => `
          <div class="notif-item ${n.is_read ? '' : 'unread'}">
            <div class="notif-item-dot" style="${n.is_read ? 'opacity:0' : ''}"></div>
            <div>
              <div class="notif-item-title">${n.title}</div>
              <div class="notif-item-msg">${n.message || ''}</div>
              <div class="notif-item-time">${n.created_at}</div>
            </div>
          </div>`).join('')
      : '<div class="notif-loading">No notifications</div>';
  } catch {}
}

// ── PROFILE DROPDOWN ──
function initProfileDropdown() {
  const btn      = document.getElementById('profile-btn');
  const dropdown = document.getElementById('profile-dropdown');
  if (!btn || !dropdown) return;
  btn.addEventListener('click', (e) => {
    e.stopPropagation();
    dropdown.classList.toggle('open');
    document.getElementById('notif-dropdown')?.classList.remove('open');
  });
  document.addEventListener('click', () => dropdown.classList.remove('open'));
  dropdown.addEventListener('click', e => e.stopPropagation());
}

// ── LOGOUT ──
function initLogout() {
  document.querySelectorAll('[data-action="logout"]').forEach(el => {
    el.addEventListener('click', async () => {
      await fetch('/api/auth/logout', { method: 'POST' });
      window.location.href = '/';
    });
  });
}

// ── SCROLL REVEAL ──
function initScrollReveal() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.08, rootMargin: '0px 0px -30px 0px' });
  document.querySelectorAll('.reveal').forEach(el => observer.observe(el));
}

// ── TOAST ──
function showToast(message, type = 'info', duration = 3000) {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    document.body.appendChild(container);
  }
  const icons = { success: '<i class="fa-solid fa-circle-check"></i>', error: '<i class="fa-solid fa-circle-xmark"></i>', info: '<i class="fa-solid fa-circle-info"></i>', warning: '<i class="fa-solid fa-triangle-exclamation"></i>' };
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `${icons[type] || ''}<span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('removing');
    setTimeout(() => toast.remove(), 250);
  }, duration);
}

// ── MODAL ──
function openModal(id) {
  document.getElementById(id)?.classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal(id) {
  document.getElementById(id)?.classList.remove('active');
  document.body.style.overflow = '';
}
document.addEventListener('click', (e) => {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// ── SKELETON ──
function showSkeleton(container, rows = 3) {
  container.innerHTML = Array(rows).fill(`
    <div style="display:flex;gap:12px;align-items:center;padding:12px 0;border-bottom:1px solid var(--border)">
      <div class="skeleton" style="width:36px;height:36px;border-radius:50%;flex-shrink:0"></div>
      <div style="flex:1">
        <div class="skeleton" style="height:13px;width:55%;margin-bottom:7px;border-radius:6px"></div>
        <div class="skeleton" style="height:11px;width:35%;border-radius:6px"></div>
      </div>
    </div>`).join('');
}

// ── FAST PAGE TRANSITIONS ──
// Uses a thin top-bar loader instead of full-page fade
// No artificial delay — navigation is instant
function initPageTransitions() {
  const bar = document.getElementById('scroll-progress');

  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href');
    if (!href || href.startsWith('#') || href.startsWith('http') || href.startsWith('mailto') || href.startsWith('javascript') || link.hasAttribute('data-action')) return;
    if (e.ctrlKey || e.metaKey || e.shiftKey) return; // allow open-in-new-tab

    // Show progress bar immediately, navigate right away
    if (bar) {
      bar.style.transition = 'none';
      bar.style.width = '30%';
      setTimeout(() => {
        bar.style.transition = 'width 0.4s ease';
        bar.style.width = '70%';
      }, 50);
    }
    // No e.preventDefault() — let the browser navigate naturally
    // The bar will be reset on next page load
  });
}

// ── THEME TOGGLE ──
function initTheme() {
  const html   = document.documentElement;
  const btn    = document.getElementById('theme-toggle');
  const icon   = document.getElementById('theme-icon');
  if (!btn || !icon) return;

  function applyTheme(theme) {
    html.setAttribute('data-theme', theme);
    localStorage.setItem('cb-theme', theme);
    if (theme === 'dark') {
      icon.className = 'fa-solid fa-sun';
      btn.title = 'Switch to Light Mode';
    } else {
      icon.className = 'fa-solid fa-moon';
      btn.title = 'Switch to Dark Mode';
    }
  }

  // Set correct icon on load
  applyTheme(localStorage.getItem('cb-theme') || 'light');

  btn.addEventListener('click', () => {
    const current = html.getAttribute('data-theme');
    applyTheme(current === 'dark' ? 'light' : 'dark');
  });
}

// ── INIT ──
document.addEventListener('DOMContentLoaded', () => {
  initScrollProgress();
  initNavbar();
  initNotifications();
  initProfileDropdown();
  initLogout();
  initScrollReveal();
  initPageTransitions();
  initTheme();

  // Quick fade-in — only 150ms, not 400ms
  document.body.style.opacity = '0';
  requestAnimationFrame(() => {
    document.body.style.transition = 'opacity 0.15s ease';
    document.body.style.opacity    = '1';
  });
});

window.CampusBot = { showToast, openModal, closeModal, showSkeleton };
