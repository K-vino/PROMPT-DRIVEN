/**
 * AgriVision AI — Shared JavaScript utilities used across all pages.
 *
 * Responsibilities:
 *   - Mobile nav toggle.
 *   - Tab bar initialisation.
 *   - Global loading / error UI helpers.
 *   - Simple Markdown-to-HTML renderer (bold, headers, lists).
 */

/* ── Mobile nav toggle ────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const links  = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
  }

  // Init any tab bars on the page
  initTabBars();
});

/* ── Tab bars ─────────────────────────────────────────────── */
function initTabBars() {
  document.querySelectorAll('.tab-bar').forEach(bar => {
    bar.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;
        // Deactivate all in this bar
        bar.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        // Find the panels (siblings of the bar's parent)
        const container = bar.parentElement || document.body;
        container.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
        const target = document.getElementById(`tab-${tabId}`);
        if (target) target.classList.add('active');
      });
    });
  });
}

/* ── Loading helpers ──────────────────────────────────────── */
/**
 * Show a spinner inside the given container element.
 * @param {HTMLElement} el
 */
function showLoading(el) {
  el.classList.remove('hidden');
  el.innerHTML = '<div class="spinner"></div>';
}

/**
 * Show an error alert inside the given container element.
 * @param {HTMLElement} el
 * @param {string} message
 */
function showError(el, message) {
  el.classList.remove('hidden');
  el.innerHTML = `
    <div class="alert alert-danger">
      <span>⚠️</span>
      <div>
        <strong>Error</strong>
        <p>${escapeHtml(message)}</p>
      </div>
    </div>`;
}

/* ── Simple Markdown renderer ─────────────────────────────── */
/**
 * Convert a subset of Markdown to safe HTML:
 *   - ## Headings
 *   - **bold**
 *   - Bullet lists (- item)
 *   - Numbered lists (1. item)
 *   - Blank lines → <p> breaks
 *
 * @param {string} text
 * @returns {string} HTML string
 */
function renderMarkdown(text) {
  if (!text) return '';
  // Escape HTML first to prevent XSS
  let html = escapeHtml(text);

  // Headings
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm,  '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm,   '<h1>$1</h1>');

  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');

  // Unordered list items
  html = html.replace(/^[*\-] (.+)$/gm, '<li>$1</li>');

  // Ordered list items
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

  // Wrap consecutive <li> in <ul>
  html = html.replace(/(<li>.*<\/li>\n?)+/g, match => `<ul>${match}</ul>`);

  // Paragraphs — double newlines
  html = html.replace(/\n{2,}/g, '</p><p>');
  html = `<p>${html}</p>`;

  // Single line breaks
  html = html.replace(/\n/g, '<br />');

  return html;
}

/* ── HTML escape ──────────────────────────────────────────── */
function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ── Weather icon mapping (OWM icon code → emoji) ─────────── */
function owmIconToEmoji(icon) {
  const map = {
    '01': '☀️', '02': '⛅', '03': '🌥️', '04': '☁️',
    '09': '🌧️', '10': '🌦️', '11': '⛈️', '13': '❄️', '50': '🌫️',
  };
  return map[icon.slice(0, 2)] || '🌡️';
}

/* ── Format Unix timestamp ─────────────────────────────────── */
function formatTime(ts) {
  return new Date(ts * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}
function formatDate(ts) {
  return new Date(ts * 1000).toLocaleDateString([], { weekday: 'short', month: 'short', day: 'numeric' });
}
