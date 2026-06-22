/**
 * StudyBuddy — Shared UI Utilities
 * Toast notifications, loading states, markdown rendering, and helpers.
 */

// ── Toast Notifications ─────────────────────────────────────────────────────
let toastContainer = null;

function getToastContainer() {
  if (!toastContainer) {
    toastContainer = document.getElementById('toast-container');
    if (!toastContainer) {
      toastContainer = document.createElement('div');
      toastContainer.id = 'toast-container';
      document.body.appendChild(toastContainer);
    }
  }
  return toastContainer;
}

const TOAST_ICONS = { success: '[OK]', error: '[X]', info: '[i]', warning: '[!]' };

export function showToast(message, type = 'info', duration = 4000) {
  const container = getToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.innerHTML = `
    <span class="toast-icon">${TOAST_ICONS[type] || '[i]'}</span>
    <span class="toast-msg">${message}</span>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), duration);
}

// ── Loading State ────────────────────────────────────────────────────────────
export function setLoading(button, loading, text = 'Loading...') {
  if (!button) return;
  if (loading) {
    button.dataset.originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = `<span class="spinner"></span> ${text}`;
  } else {
    button.disabled = false;
    button.innerHTML = button.dataset.originalText || text;
  }
}

// ── Skeleton Loader ──────────────────────────────────────────────────────────
export function renderSkeletons(container, count = 3, height = '120px') {
  container.innerHTML = Array(count).fill(0).map(() =>
    `<div class="skeleton" style="height:${height};border-radius:12px;"></div>`
  ).join('');
}

// ── Markdown Renderer ────────────────────────────────────────────────────────
export function renderMarkdown(md) {
  if (!md) return '';
  let html = md
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    // Headings
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    // Bold / Italic
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/_(.+?)_/g, '<em>$1</em>')
    // Code blocks
    .replace(/```([\w]*)\n([\s\S]+?)```/gm, '<pre><code class="lang-$1">$2</code></pre>')
    .replace(/`([^`]+)`/g, '<code>$1</code>')
    // Blockquote
    .replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')
    // Horizontal rule
    .replace(/^---$/gm, '<hr>')
    // Unordered list
    .replace(/^\s*[-*] (.+)$/gm, '<li>$1</li>')
    // Ordered list
    .replace(/^\d+\. (.+)$/gm, '<li>$1</li>')
    // Paragraphs
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>[\s\S]+?<\/li>)+/g, m => `<ul>${m}</ul>`);
  return `<p>${html}</p>`;
}

// ── Download Blob as File ────────────────────────────────────────────────────
export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

// ── Date Formatter ───────────────────────────────────────────────────────────
export function formatDate(isoString) {
  if (!isoString) return '';
  const d = new Date(isoString);
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

// ── Relative Time ─────────────────────────────────────────────────────────────
export function timeAgo(isoString) {
  const secs = Math.floor((Date.now() - new Date(isoString)) / 1000);
  if (secs < 60)  return 'just now';
  if (secs < 3600) return `${Math.floor(secs/60)}m ago`;
  if (secs < 86400) return `${Math.floor(secs/3600)}h ago`;
  return `${Math.floor(secs/86400)}d ago`;
}

// ── Difficulty Badge ─────────────────────────────────────────────────────────
export function difficultyBadge(level) {
  const map = { easy: 'success', medium: 'warning', hard: 'danger' };
  return `<span class="badge badge-${map[level] || 'primary'}">${level}</span>`;
}

// ── Confirm Modal ────────────────────────────────────────────────────────────
export function confirm(message) {
  return new Promise(resolve => {
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay open';
    overlay.innerHTML = `
      <div class="modal" style="max-width:380px;text-align:center;">
        <h3 style="margin-bottom:0.5rem;">Confirm</h3>
        <p style="color:var(--text-muted);margin-bottom:1.5rem;">${message}</p>
        <div class="flex gap-1 justify-center">
          <button id="cf-cancel" class="btn btn-secondary">Cancel</button>
          <button id="cf-ok" class="btn btn-danger">Delete</button>
        </div>
      </div>`;
    document.body.appendChild(overlay);
    overlay.querySelector('#cf-cancel').onclick = () => { overlay.remove(); resolve(false); };
    overlay.querySelector('#cf-ok').onclick    = () => { overlay.remove(); resolve(true);  };
  });
}

// ── Escape HTML ──────────────────────────────────────────────────────────────
export function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}
