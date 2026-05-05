/**
 * AgriVision AI — Plant Identifier page JS
 *
 * Responsibilities:
 *   - Handle drag-and-drop and file picker upload.
 *   - Handle URL-based identification.
 *   - Handle plant care search.
 *   - Render identification and care results.
 */

document.addEventListener('DOMContentLoaded', () => {
  /* ── Upload tab ─────────────────────────────────────────── */
  const uploadZone    = document.getElementById('uploadZone');
  const fileInput     = document.getElementById('fileInput');
  const identifyBtn   = document.getElementById('identifyUploadBtn');
  const imagePreview  = document.getElementById('imagePreview');
  const results       = document.getElementById('identifyResults');

  let selectedFile = null;

  // File picker
  fileInput?.addEventListener('change', () => {
    selectedFile = fileInput.files[0] || null;
    previewFile(selectedFile);
    if (identifyBtn) identifyBtn.disabled = !selectedFile;
  });

  // Drag & drop
  uploadZone?.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone?.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone?.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    selectedFile = e.dataTransfer.files[0] || null;
    previewFile(selectedFile);
    if (identifyBtn) identifyBtn.disabled = !selectedFile;
  });
  uploadZone?.addEventListener('click', e => {
    if (e.target !== fileInput) fileInput?.click();
  });

  identifyBtn?.addEventListener('click', async () => {
    if (!selectedFile) return;
    const organs = getCheckedOrgans('organ');
    showLoading(results);
    try {
      const res = await PlantAPI.identifyFromFile(selectedFile, organs);
      renderIdentificationResults(res.data, results);
    } catch (err) {
      showError(results, err.message);
    }
  });

  /* ── URL tab ────────────────────────────────────────────── */
  const urlInput   = document.getElementById('imageUrl');
  const identifyUrlBtn = document.getElementById('identifyUrlBtn');

  identifyUrlBtn?.addEventListener('click', async () => {
    const url = urlInput?.value.trim();
    if (!url) return;
    const organs = getCheckedOrgans('organUrl');
    showLoading(results);
    try {
      const res = await PlantAPI.identifyFromUrl(url, organs);
      renderIdentificationResults(res.data, results);
    } catch (err) {
      showError(results, err.message);
    }
  });

  /* ── Care search tab ────────────────────────────────────── */
  const careSearchInput = document.getElementById('careSearch');
  const careSearchBtn   = document.getElementById('careSearchBtn');

  careSearchBtn?.addEventListener('click', searchCare);
  careSearchInput?.addEventListener('keydown', e => { if (e.key === 'Enter') searchCare(); });

  async function searchCare() {
    const q = careSearchInput?.value.trim();
    if (!q) return;
    showLoading(results);
    try {
      const res = await PlantAPI.searchCare(q);
      renderCareResults(res.data.results, results);
    } catch (err) {
      showError(results, err.message);
    }
  }

  /* ── Helpers ────────────────────────────────────────────── */
  function previewFile(file) {
    if (!file || !imagePreview) return;
    const reader = new FileReader();
    reader.onload = e => {
      imagePreview.classList.remove('hidden');
      imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
    };
    reader.readAsDataURL(file);
  }

  function getCheckedOrgans(name) {
    const checked = [...document.querySelectorAll(`input[name="${name}"]:checked`)].map(i => i.value);
    return checked.length ? checked : ['auto'];
  }
});

/* ── Render functions ─────────────────────────────────────── */
function renderIdentificationResults(data, container) {
  if (!data) { showError(container, 'No results returned.'); return; }
  const { best_match, candidates } = data;

  let html = `<h2 class="section-subtitle">Identification Results</h2>`;

  // Best match highlight
  html += `
    <div class="alert alert-success">
      ✅ Best match: <strong>${escapeHtml(best_match.species_name)}</strong>
      (${Math.round(best_match.score * 100)}% confidence)
    </div>`;

  // All candidates
  candidates.forEach((match, i) => {
    const imgHtml = match.image_url
      ? `<img src="${escapeHtml(match.image_url)}" class="result-card-image" alt="${escapeHtml(match.species_name)}" />`
      : `<div class="result-card-image" style="background:#e8f0eb;display:flex;align-items:center;justify-content:center;font-size:2rem">🌿</div>`;

    html += `
      <div class="result-card">
        ${imgHtml}
        <div class="result-card-body">
          <h3>${escapeHtml(match.species_name)}</h3>
          ${match.common_names.length ? `<p class="common-names">Also known as: ${escapeHtml(match.common_names.join(', '))}</p>` : ''}
          ${match.family ? `<p class="text-muted" style="font-size:.85rem;margin-top:4px">Family: ${escapeHtml(match.family)}</p>` : ''}
          <div class="confidence-bar-wrap">
            <div class="confidence-bar">
              <div class="confidence-fill" style="width:${Math.round(match.score*100)}%"></div>
            </div>
            <span class="confidence-label">${Math.round(match.score*100)}%</span>
          </div>
        </div>
      </div>`;
  });

  container.classList.remove('hidden');
  container.innerHTML = html;
}

function renderCareResults(plants, container) {
  if (!plants || plants.length === 0) {
    container.classList.remove('hidden');
    container.innerHTML = '<div class="alert alert-info">No plants found for your search.</div>';
    return;
  }

  let html = `<h2 class="section-subtitle">Plant Care Results (${plants.length})</h2>`;
  plants.forEach(p => {
    const img = p.image_url
      ? `<img src="${escapeHtml(p.image_url)}" class="care-card-img" alt="${escapeHtml(p.common_name)}" />`
      : `<div class="care-card-img" style="background:#e8f0eb;display:flex;align-items:center;justify-content:center;font-size:2.5rem">🌿</div>`;

    const attrs = [];
    if (p.watering)    attrs.push(`💧 ${escapeHtml(p.watering)}`);
    if (p.care_level)  attrs.push(`⭐ ${escapeHtml(p.care_level)}`);
    if (p.growth_rate) attrs.push(`📈 ${escapeHtml(p.growth_rate)}`);
    if (p.sunlight.length) attrs.push(`☀️ ${escapeHtml(p.sunlight.join(', '))}`);

    html += `
      <div class="care-card">
        ${img}
        <div>
          <h3>${escapeHtml(p.common_name)}</h3>
          <p class="text-muted" style="font-size:.85rem;margin-bottom:.5rem">${escapeHtml((p.scientific_name || []).join(', '))}</p>
          <div class="care-attrs">${attrs.map(a => `<span class="care-attr">${a}</span>`).join('')}</div>
          ${p.description ? `<p style="margin-top:.5rem;font-size:.9rem">${escapeHtml(p.description.slice(0, 200))}${p.description.length > 200 ? '…' : ''}</p>` : ''}
        </div>
      </div>`;
  });

  container.classList.remove('hidden');
  container.innerHTML = html;
}
