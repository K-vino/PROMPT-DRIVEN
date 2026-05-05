/**
 * AgriVision AI — Dashboard page JS
 *
 * Responsibilities:
 *   - Quick weather widget (search by city).
 */

document.addEventListener('DOMContentLoaded', () => {
  const cityInput    = document.getElementById('weatherCity');
  const searchBtn    = document.getElementById('weatherSearchBtn');
  const resultBox    = document.getElementById('weatherWidgetResult');

  if (!searchBtn) return;

  searchBtn.addEventListener('click', fetchWidgetWeather);
  cityInput.addEventListener('keydown', e => { if (e.key === 'Enter') fetchWidgetWeather(); });

  async function fetchWidgetWeather() {
    const city = cityInput.value.trim();
    if (!city) return;

    showLoading(resultBox);
    try {
      const res = await WeatherAPI.getCurrentByCity(city);
      const w = res.data;
      const icon = owmIconToEmoji(w.conditions[0]?.icon || '01d');
      resultBox.innerHTML = `
        <div style="display:flex;align-items:center;gap:1rem;color:#fff;">
          <span style="font-size:3rem">${icon}</span>
          <div>
            <div style="font-size:1.5rem;font-weight:800">${Math.round(w.temperature)}°C</div>
            <div style="font-size:1rem;opacity:.9">${w.city}, ${w.country}</div>
            <div style="font-size:.9rem;opacity:.75;text-transform:capitalize">${w.conditions[0]?.description || ''}</div>
          </div>
          <div style="margin-left:auto;text-align:right;font-size:.9rem;opacity:.8;">
            💧 ${w.humidity}%<br/>
            💨 ${w.wind_speed} m/s
          </div>
        </div>`;
    } catch (err) {
      resultBox.innerHTML = `<div style="color:#ffcdd2">⚠️ ${escapeHtml(err.message)}</div>`;
    }
  }
});
