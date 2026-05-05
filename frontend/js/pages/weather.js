/**
 * AgriVision AI — Weather page JS
 *
 * Responsibilities:
 *   - Search weather by city name or geolocation.
 *   - Display current weather card.
 *   - Display 5-day forecast strip.
 *   - Fetch and display AI farm insight.
 */

document.addEventListener('DOMContentLoaded', () => {
  const cityInput     = document.getElementById('cityInput');
  const searchBtn     = document.getElementById('searchWeatherBtn');
  const geoBtn        = document.getElementById('geoWeatherBtn');
  const currentCard   = document.getElementById('currentWeatherCard');
  const forecastStrip = document.getElementById('forecastStrip');
  const insightCard   = document.getElementById('farmInsightCard');
  const getInsightBtn = document.getElementById('getInsightBtn');
  const insightText   = document.getElementById('insightText');

  let lastCity = '';
  let lastLat = null, lastLon = null;

  searchBtn?.addEventListener('click', () => {
    const city = cityInput?.value.trim();
    if (city) fetchWeatherByCity(city);
  });
  cityInput?.addEventListener('keydown', e => {
    if (e.key === 'Enter') searchBtn.click();
  });

  geoBtn?.addEventListener('click', () => {
    if (!navigator.geolocation) return alert('Geolocation not supported by your browser.');
    navigator.geolocation.getCurrentPosition(
      pos => fetchWeatherByCoords(pos.coords.latitude, pos.coords.longitude),
      () => alert('Could not get your location.'),
    );
  });

  getInsightBtn?.addEventListener('click', fetchInsight);

  /* ── Fetch functions ──────────────────────────────────────── */
  async function fetchWeatherByCity(city) {
    lastCity = city; lastLat = null; lastLon = null;
    try {
      const [curRes, foreRes] = await Promise.all([
        WeatherAPI.getCurrentByCity(city),
        WeatherAPI.getForecastByCity(city),
      ]);
      renderCurrentWeather(curRes.data);
      renderForecast(foreRes.data);
      insightCard.classList.remove('hidden');
    } catch (err) {
      alert(`Error fetching weather: ${err.message}`);
    }
  }

  async function fetchWeatherByCoords(lat, lon) {
    lastLat = lat; lastLon = lon; lastCity = '';
    try {
      const [curRes, foreRes] = await Promise.all([
        WeatherAPI.getCurrentByCoords(lat, lon),
        WeatherAPI.getForecastByCoords(lat, lon),
      ]);
      renderCurrentWeather(curRes.data);
      renderForecast(foreRes.data);
      insightCard.classList.remove('hidden');
    } catch (err) {
      alert(`Error fetching weather: ${err.message}`);
    }
  }

  async function fetchInsight() {
    const crop = document.getElementById('insightCrop')?.value.trim() || '';
    insightText.innerHTML = '<div class="spinner"></div>';
    try {
      let res;
      if (lastCity) {
        res = await WeatherAPI.getInsight(lastCity, crop);
      } else {
        res = await WeatherAPI.getInsightByCoords(lastLat, lastLon, crop);
      }
      insightText.innerHTML = `<div class="markdown-body">${renderMarkdown(res.data)}</div>`;
    } catch (err) {
      insightText.innerHTML = `<div class="alert alert-danger">⚠️ ${escapeHtml(err.message)}</div>`;
    }
  }

  /* ── Render helpers ──────────────────────────────────────── */
  function renderCurrentWeather(w) {
    const cond = w.conditions[0] || {};
    const icon = owmIconToEmoji(cond.icon || '01d');

    document.getElementById('weatherIconLg').textContent   = icon;
    document.getElementById('weatherTemp').textContent     = `${Math.round(w.temperature)}°C`;
    document.getElementById('weatherFeels').textContent    = `Feels like ${Math.round(w.feels_like)}°C`;
    document.getElementById('weatherDesc').textContent     = cond.description || '';
    document.getElementById('weatherHumidity').textContent = `${w.humidity}%`;
    document.getElementById('weatherWind').textContent     = `${w.wind_speed} m/s`;
    document.getElementById('weatherPressure').textContent = `${w.pressure} hPa`;
    document.getElementById('weatherVisibility').textContent = `${(w.visibility / 1000).toFixed(1)} km`;

    // Update title with city name
    const h1 = document.querySelector('.page-header h1');
    if (h1) h1.textContent = `⛅ ${w.city}, ${w.country}`;

    currentCard.classList.remove('hidden');
  }

  function renderForecast(forecast) {
    const grid = document.getElementById('forecastGrid');
    if (!grid) return;

    grid.innerHTML = forecast.entries.map(entry => {
      const icon = owmIconToEmoji(entry.conditions[0]?.icon || '01d');
      const desc = entry.conditions[0]?.description || '';
      const rain = entry.rain_3h > 0 ? `🌧️ ${entry.rain_3h.toFixed(1)} mm` : '';
      return `
        <div class="forecast-card">
          <div class="fc-time">${formatDate(entry.timestamp)}<br/>${formatTime(entry.timestamp)}</div>
          <div class="fc-icon">${icon}</div>
          <div class="fc-temp">${Math.round(entry.temperature)}°C</div>
          <div style="font-size:.8rem;color:#666;text-transform:capitalize">${escapeHtml(desc)}</div>
          ${rain ? `<div class="fc-rain">${rain}</div>` : ''}
        </div>`;
    }).join('');

    forecastStrip.classList.remove('hidden');
  }
});
