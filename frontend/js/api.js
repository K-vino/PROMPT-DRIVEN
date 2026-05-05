/**
 * AgriVision AI — Unified API Client
 *
 * Responsibilities:
 *   - Centralise all HTTP calls to the FastAPI backend.
 *   - Provide typed helper methods for each feature domain.
 *   - Handle errors uniformly and throw descriptive Error objects.
 */

const API_BASE = window.location.origin + '/api/v1';

/* ── Generic request helper ───────────────────────────────── */
async function apiFetch(path, options = {}) {
  const url = `${API_BASE}${path}`;
  let response;
  try {
    response = await fetch(url, {
      headers: { 'Accept': 'application/json', ...options.headers },
      ...options,
    });
  } catch (networkErr) {
    throw new Error(`Network error: ${networkErr.message}`);
  }

  const contentType = response.headers.get('content-type') || '';
  const data = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = (data && data.error) || (data && data.detail) || response.statusText;
    throw new Error(`[${response.status}] ${message}`);
  }
  return data;
}

/* ── Plant Identification ─────────────────────────────────── */
const PlantAPI = {
  /**
   * Identify a plant from a File object.
   * @param {File} file
   * @param {string[]} organs  e.g. ['leaf', 'flower']
   */
  async identifyFromFile(file, organs = ['auto']) {
    const form = new FormData();
    form.append('file', file);
    form.append('organs', organs.join(','));
    return apiFetch('/plants/identify/upload', { method: 'POST', body: form });
  },

  /**
   * Identify a plant from a URL string.
   * @param {string} imageUrl
   * @param {string[]} organs
   */
  async identifyFromUrl(imageUrl, organs = ['auto']) {
    return apiFetch('/plants/identify/url', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ image_url: imageUrl, organs }),
    });
  },

  /** Search plant care information by name. */
  async searchCare(query, page = 1) {
    return apiFetch(`/plants/care/search?q=${encodeURIComponent(query)}&page=${page}`);
  },

  /** Get detailed care info for a Perenual species ID. */
  async getCarById(plantId) {
    return apiFetch(`/plants/care/${plantId}`);
  },
};

/* ── Disease Detection ────────────────────────────────────── */
const DiseaseAPI = {
  /**
   * Detect disease from an uploaded image File.
   * @param {File} file
   * @param {string} plantName  Optional known plant name.
   */
  async detectFromFile(file, plantName = '') {
    const form = new FormData();
    form.append('file', file);
    if (plantName) form.append('plant_name', plantName);
    return apiFetch('/disease/detect/upload', { method: 'POST', body: form });
  },

  /**
   * Analyse symptoms described in text.
   * @param {string} plantName
   * @param {string} symptoms
   * @param {string} imageDescription
   */
  async analyseSymptoms(plantName, symptoms, imageDescription = '') {
    return apiFetch('/disease/analyse', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ plant_name: plantName, symptoms, image_description: imageDescription }),
    });
  },
};

/* ── Weather ──────────────────────────────────────────────── */
const WeatherAPI = {
  /** Fetch current weather by city name. */
  async getCurrentByCity(city) {
    return apiFetch(`/weather/current?city=${encodeURIComponent(city)}`);
  },

  /** Fetch current weather by coordinates. */
  async getCurrentByCoords(lat, lon) {
    return apiFetch(`/weather/current?lat=${lat}&lon=${lon}`);
  },

  /** Fetch forecast by city name. */
  async getForecastByCity(city, days = 5) {
    return apiFetch(`/weather/forecast?city=${encodeURIComponent(city)}&days=${days}`);
  },

  /** Fetch forecast by coordinates. */
  async getForecastByCoords(lat, lon, days = 5) {
    return apiFetch(`/weather/forecast?lat=${lat}&lon=${lon}&days=${days}`);
  },

  /** Get AI farming insight for a city. */
  async getInsight(city, crop = '') {
    const cropParam = crop ? `&crop=${encodeURIComponent(crop)}` : '';
    return apiFetch(`/weather/insight?city=${encodeURIComponent(city)}${cropParam}`);
  },

  /** Get AI farming insight by coordinates. */
  async getInsightByCoords(lat, lon, crop = '') {
    const cropParam = crop ? `&crop=${encodeURIComponent(crop)}` : '';
    return apiFetch(`/weather/insight?lat=${lat}&lon=${lon}${cropParam}`);
  },
};

/* ── AI Advisor ───────────────────────────────────────────── */
const AdvisorAPI = {
  /**
   * Ask a single question.
   * @param {string} question
   */
  async ask(question) {
    return apiFetch('/advisor/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
  },

  /**
   * Send a full conversation history for multi-turn chat.
   * @param {{ role: string, text: string }[]} messages
   */
  async chat(messages) {
    return apiFetch('/advisor/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ messages }),
    });
  },

  /**
   * Get a crop-specific advisory.
   * @param {Object} params
   */
  async cropAdvisory({ crop, location, soil_type = '', season = '', issue = '' }) {
    return apiFetch('/advisor/crop', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ crop, location, soil_type, season, issue }),
    });
  },
};

/* ── Crops ────────────────────────────────────────────────── */
const CropsAPI = {
  /** List all supported crops, optionally filtered. */
  async list(category = '', season = '') {
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    if (season)   params.set('season', season);
    const qs = params.toString() ? `?${params}` : '';
    return apiFetch(`/crops/${qs}`);
  },

  /** Get an AI overview for a crop by name. */
  async getInfo(cropName) {
    return apiFetch(`/crops/${encodeURIComponent(cropName)}`);
  },

  /** Generate an AI planting plan. */
  async generatePlan(cropName, planDetails) {
    return apiFetch(`/crops/${encodeURIComponent(cropName)}/plan`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(planDetails),
    });
  },

  /** Get pest & disease guide for a crop. */
  async getPests(cropName) {
    return apiFetch(`/crops/${encodeURIComponent(cropName)}/pests`);
  },
};
