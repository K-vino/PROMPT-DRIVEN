/**
 * AgriVision AI — AI Advisor page JS
 *
 * Responsibilities:
 *   - Manage multi-turn chat conversation state.
 *   - Render user and AI messages in the chat window.
 *   - Handle quick-prompt chips.
 *   - Auto-resize textarea and scroll to latest message.
 */

document.addEventListener('DOMContentLoaded', () => {
  const chatWindow  = document.getElementById('chatWindow');
  const chatForm    = document.getElementById('chatForm');
  const chatInput   = document.getElementById('chatInput');
  const clearBtn    = document.getElementById('clearChatBtn');

  // Conversation history: [{ role: 'user'|'model', text: '...' }]
  let history = [];

  /* ── Send message ─────────────────────────────────────────── */
  chatForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const text = chatInput.value.trim();
    if (!text) return;
    sendMessage(text);
  });

  async function sendMessage(text) {
    chatInput.value = '';
    resizeTextarea();

    // Append user message
    history.push({ role: 'user', text });
    appendMessage('user', text);

    // Typing indicator
    const typingEl = appendMessage('bot', '…', true);

    try {
      const res = await AdvisorAPI.chat(history);
      const reply = res.data;
      history.push({ role: 'model', text: reply });
      typingEl.querySelector('.msg-bubble').innerHTML = renderMarkdown(reply);
      typingEl.querySelector('.msg-bubble').classList.remove('typing');
    } catch (err) {
      typingEl.querySelector('.msg-bubble').innerHTML =
        `<span style="color:var(--color-danger)">⚠️ ${escapeHtml(err.message)}</span>`;
      typingEl.querySelector('.msg-bubble').classList.remove('typing');
      // Remove failed turn from history
      history.pop();
    }
    scrollBottom();
  }

  /* ── Quick prompt chips ──────────────────────────────────── */
  document.querySelectorAll('.prompt-chip').forEach(chip => {
    chip.addEventListener('click', () => {
      const prompt = chip.dataset.prompt;
      if (prompt) sendMessage(prompt);
    });
  });

  /* ── Clear chat ───────────────────────────────────────────── */
  clearBtn?.addEventListener('click', () => {
    history = [];
    // Keep only the first welcome message
    const msgs = chatWindow.querySelectorAll('.chat-message');
    msgs.forEach((m, i) => { if (i > 0) m.remove(); });
  });

  /* ── Textarea auto-resize ────────────────────────────────── */
  chatInput?.addEventListener('input', resizeTextarea);
  chatInput?.addEventListener('keydown', e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      chatForm.dispatchEvent(new Event('submit'));
    }
  });

  function resizeTextarea() {
    if (!chatInput) return;
    chatInput.style.height = 'auto';
    chatInput.style.height = Math.min(chatInput.scrollHeight, 150) + 'px';
  }

  /* ── Helpers ─────────────────────────────────────────────── */
  function appendMessage(role, text, isTyping = false) {
    const div = document.createElement('div');
    div.className = `chat-message ${role}`;
    div.innerHTML = `
      <div class="msg-bubble${isTyping ? ' typing' : ''}">
        ${isTyping ? escapeHtml(text) : renderMarkdown(text)}
      </div>`;
    chatWindow.appendChild(div);
    scrollBottom();
    return div;
  }

  function scrollBottom() {
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }
});
