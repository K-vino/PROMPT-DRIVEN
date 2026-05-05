/**
 * AgriVision AI — Crop Planner page JS
 *
 * Responsibilities:
 *   - Fetch and display the crop list with filtering.
 *   - Handle crop card clicks (show info + pest guide).
 *   - Generate AI planting plans.
 */

document.addEventListener('DOMContentLoaded', () => {
  const cropGrid      = document.getElementById('cropGrid');
  const cropSearch    = document.getElementById('cropSearch');
  const categoryFilter = document.getElementById('categoryFilter');
  const seasonFilter  = document.getElementById('seasonFilter');
  const planForm      = document.getElementById('planForm');
  const planResult    = document.getElementById('planResult');

  // Crop icons mapping
  const CROP_ICONS = {
    'Wheat': '🌾', 'Rice': '🌾', 'Maize': '🌽', 'Tomato': '🍅',
    'Potato': '🥔', 'Onion': '🧅', 'Soybean': '🫘', 'Chickpea': '🫘',
    'Cotton': '☁️', 'Sugarcane': '🎋', 'Banana': '🍌', 'Mango': '🥭',
  };

  let allCrops = [];

  /* ── Load crops ───────────────────────────────────────────── */
  loadCrops();

  async function loadCrops() {
    try {
      const res = await CropsAPI.list();
      allCrops = res.data;
      renderCrops(allCrops);
    } catch (err) {
      cropGrid.innerHTML = `<div class="alert alert-danger col-span-all">⚠️ ${escapeHtml(err.message)}</div>`;
    }
  }

  /* ── Filters ─────────────────────────────────────────────── */
  cropSearch?.addEventListener('input', applyFilters);
  categoryFilter?.addEventListener('change', applyFilters);
  seasonFilter?.addEventListener('change', applyFilters);

  function applyFilters() {
    const q    = cropSearch?.value.toLowerCase() || '';
    const cat  = categoryFilter?.value || '';
    const seas = seasonFilter?.value || '';
    const filtered = allCrops.filter(c => {
      const matchQ   = !q    || c.name.toLowerCase().includes(q);
      const matchCat = !cat  || c.category === cat;
      const matchS   = !seas || c.seasons.includes(seas);
      return matchQ && matchCat && matchS;
    });
    renderCrops(filtered);
  }

  /* ── Render crop grid ────────────────────────────────────── */
  function renderCrops(crops) {
    if (!crops.length) {
      cropGrid.innerHTML = '<p class="text-muted">No crops match your filters.</p>';
      return;
    }
    cropGrid.innerHTML = crops.map(c => `
      <div class="crop-card" data-crop="${escapeHtml(c.name)}">
        <div class="crop-card-icon">${CROP_ICONS[c.name] || '🌱'}</div>
        <h3>${escapeHtml(c.name)}</h3>
        <p class="text-muted" style="font-size:.85rem">${escapeHtml(c.category)}</p>
        <div class="seasons">
          ${c.seasons.map(s => `<span class="season-tag">${escapeHtml(s)}</span>`).join('')}
        </div>
      </div>`).join('');

    // Click to pre-fill planner & show info
    cropGrid.querySelectorAll('.crop-card').forEach(card => {
      card.addEventListener('click', () => {
        const name = card.dataset.crop;
        const planCropInput = document.getElementById('planCrop');
        if (planCropInput) planCropInput.value = name;
        document.getElementById('plannerSection')?.scrollIntoView({ behavior: 'smooth' });
      });
    });
  }

  /* ── AI Planting Plan ─────────────────────────────────────── */
  planForm?.addEventListener('submit', async e => {
    e.preventDefault();
    const cropName = document.getElementById('planCrop')?.value.trim();
    const location = document.getElementById('planLocation')?.value.trim();
    if (!cropName || !location) return;

    showLoading(planResult);
    try {
      const res = await CropsAPI.generatePlan(cropName, {
        location,
        soil_type:             document.getElementById('planSoil')?.value.trim() || '',
        farm_size_hectares:    parseFloat(document.getElementById('planSize')?.value) || 1,
        available_water:       document.getElementById('planWater')?.value || '',
        budget_level:          document.getElementById('planBudget')?.value || '',
      });
      planResult.classList.remove('hidden');
      planResult.innerHTML = `
        <div class="card">
          <h3 style="margin-bottom:1rem;color:var(--color-primary)">🌾 AI Planting Plan — ${escapeHtml(cropName)}</h3>
          <div class="markdown-body">${renderMarkdown(res.data)}</div>
        </div>`;
    } catch (err) {
      showError(planResult, err.message);
    }
  });
});
