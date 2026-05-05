/**
 * AgriVision AI — Disease Detector page JS
 *
 * Responsibilities:
 *   - Handle image upload and preview.
 *   - Call the Disease API for image-based and symptom-based analysis.
 *   - Render AI recommendations.
 */

document.addEventListener('DOMContentLoaded', () => {
  /* ── Image detection tab ─────────────────────────────────── */
  const uploadZone     = document.getElementById('diseaseUploadZone');
  const fileInput      = document.getElementById('diseaseFileInput');
  const detectBtn      = document.getElementById('detectDiseaseBtn');
  const plantNameInput = document.getElementById('knownPlantName');
  const imgPreview     = document.getElementById('diseaseImagePreview');
  const results        = document.getElementById('diseaseResults');

  let selectedFile = null;

  fileInput?.addEventListener('change', () => {
    selectedFile = fileInput.files[0] || null;
    previewFile(selectedFile, imgPreview);
    if (detectBtn) detectBtn.disabled = !selectedFile;
  });

  uploadZone?.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
  uploadZone?.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
  uploadZone?.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    selectedFile = e.dataTransfer.files[0] || null;
    previewFile(selectedFile, imgPreview);
    if (detectBtn) detectBtn.disabled = !selectedFile;
  });

  detectBtn?.addEventListener('click', async () => {
    if (!selectedFile) return;
    const plantName = plantNameInput?.value.trim() || '';
    showLoading(results);
    try {
      const res = await DiseaseAPI.detectFromFile(selectedFile, plantName);
      renderDiseaseResult(res.data, results);
    } catch (err) {
      showError(results, err.message);
    }
  });

  /* ── Symptom checker tab ─────────────────────────────────── */
  const analyseBtn    = document.getElementById('analyseSymptomBtn');
  const plantInput    = document.getElementById('symptomPlantName');
  const symptomsInput = document.getElementById('symptoms');
  const imgDescInput  = document.getElementById('imgDescription');

  analyseBtn?.addEventListener('click', async () => {
    const plant    = plantInput?.value.trim();
    const symptoms = symptomsInput?.value.trim();
    if (!plant || !symptoms) {
      alert('Please enter both plant name and symptoms.');
      return;
    }
    showLoading(results);
    try {
      const res = await DiseaseAPI.analyseSymptoms(plant, symptoms, imgDescInput?.value.trim() || '');
      renderDiseaseResult(res.data, results);
    } catch (err) {
      showError(results, err.message);
    }
  });

  /* ── Helpers ─────────────────────────────────────────────── */
  function previewFile(file, previewEl) {
    if (!file || !previewEl) return;
    const reader = new FileReader();
    reader.onload = e => {
      previewEl.classList.remove('hidden');
      previewEl.innerHTML = `<img src="${e.target.result}" alt="Preview" />`;
    };
    reader.readAsDataURL(file);
  }
});

function renderDiseaseResult(data, container) {
  const statusClass = data.is_healthy ? 'healthy' : 'sick';
  const statusText  = data.is_healthy ? '✅ Plant appears healthy' : '⚠️ Potential disease detected';

  let html = `
    <div class="disease-result">
      <div class="disease-status ${statusClass}">${statusText}</div>`;

  if (data.ai_recommendation) {
    html += `
      <div class="ai-recommendation">
        <h4>🤖 AI Analysis &amp; Recommendations</h4>
        <div class="markdown-body">${renderMarkdown(data.ai_recommendation)}</div>
      </div>`;
  }

  html += '</div>';
  container.classList.remove('hidden');
  container.innerHTML = html;
}
