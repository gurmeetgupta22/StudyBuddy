/**
 * StudyBuddy — Sidebar Component
 * Renders the sidebar and handles navigation state + dark mode toggle.
 */
import { getUser, clearToken } from './api.js';
import { pageUrl } from './routes.js';

const NAV_ITEMS = [
  { label: 'Main', section: true },
  { id: 'dashboard', label: 'Dashboard',  icon: 'D', href: pageUrl('dashboard') },
  { id: 'notes',     label: 'Study Notes', icon: 'N', href: pageUrl('notes') },
  { id: 'test',      label: 'Tests',       icon: 'T', href: pageUrl('test') },
  { label: 'Insights', section: true },
  { id: 'history',   label: 'History',     icon: 'H', href: pageUrl('history') },
  { id: 'analytics', label: 'Analytics',   icon: 'A', href: pageUrl('analytics') },
];

export function renderSidebar(activeId) {
  const user = getUser();
  const avatarHtml = user?.avatar_url
    ? `<img src="${user.avatar_url}" alt="avatar">`
    : `<div style="width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--primary),var(--accent));display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.9rem;color:white;font-family:var(--font-sans);">${(user?.name || 'U')[0]}</div>`;

  const navHtml = NAV_ITEMS.map(item => {
    if (item.section) {
      return `<div class="nav-section-label">${item.label}</div>`;
    }
    const active = item.id === activeId ? 'active' : '';
    return `<a href="${item.href}" class="nav-item ${active}" id="nav-${item.id}">
      <span class="nav-icon">${item.icon}</span>
      <span>${item.label}</span>
    </a>`;
  }).join('');

  const isDark = document.documentElement.getAttribute('data-theme') !== 'light';

  const sidebar = document.createElement('aside');
  sidebar.className = 'sidebar';
  sidebar.id = 'sidebar';
  sidebar.innerHTML = `
    <div class="sidebar-logo">
      <div class="logo-icon"><img src="/frontend/assets/logo.png" alt="StudyBuddy"></div>
      <span>StudyBuddy</span>
    </div>
    <div class="sidebar-user">
      ${avatarHtml}
      <div class="user-info">
        <div class="user-name">${user?.name || 'Student'}</div>
        <div class="user-email">${user?.email || ''}</div>
      </div>
    </div>
    <nav class="sidebar-nav">${navHtml}</nav>
    <div class="sidebar-footer">
      <button class="btn btn-ghost btn-sm" id="theme-toggle">
        ${isDark ? 'Light Mode' : 'Dark Mode'}
      </button>
      <button class="btn btn-ghost btn-sm" id="sidebar-logout">
        Logout
      </button>
    </div>
  `;
  document.body.prepend(sidebar);

  // Mobile backdrop
  const backdrop = document.createElement('div');
  backdrop.className = 'sidebar-backdrop';
  backdrop.id = 'sidebar-backdrop';
  document.body.prepend(backdrop);

  // Mobile toggle button
  const toggle = document.createElement('button');
  toggle.className = 'mobile-nav-toggle';
  toggle.id = 'mobile-toggle';
  toggle.textContent = '=';
  document.body.prepend(toggle);

  // Events
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  document.getElementById('sidebar-logout').addEventListener('click', logout);
  toggle.addEventListener('click', () => {
    sidebar.classList.toggle('open');
    backdrop.classList.toggle('open');
  });
  backdrop.addEventListener('click', () => {
    sidebar.classList.remove('open');
    backdrop.classList.remove('open');
  });
}

function toggleTheme() {
  const html = document.documentElement;
  const isLight = html.getAttribute('data-theme') === 'light';
  html.setAttribute('data-theme', isLight ? 'dark' : 'light');
  localStorage.setItem('sb_theme', isLight ? 'dark' : 'light');
  document.getElementById('theme-toggle').textContent =
    isLight ? 'Light Mode' : 'Dark Mode';
}

function logout() {
  clearToken();
  window.location.href = pageUrl('index');
}

// Apply saved theme on load
export function applyTheme() {
  const saved = localStorage.getItem('sb_theme') || 'dark';
  document.documentElement.setAttribute('data-theme', saved);
}

// Guard: redirect to login if no token
export function requireAuth() {
  const token = localStorage.getItem('sb_token');
  if (!token) {
    window.location.href = pageUrl('index');
    return false;
  }
  return true;
}
