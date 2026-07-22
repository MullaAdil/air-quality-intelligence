console.log("SCRIPT VERSION:", Date.now());
let API_BASE = "http://localhost:5050";

// AQI color thresholds
const AQI_LEVELS = [
  { max: 50, color: "#22c55e", label: "Good" },
  { max: 100, color: "#eab308", label: "Moderate" },
  { max: 150, color: "#f97316", label: "Unhealthy for Sensitive" },
  { max: 200, color: "#ef4444", label: "Unhealthy" },
  { max: 300, color: "#a855f7", label: "Very Unhealthy" },
  { max: Infinity, color: "#7f1d1d", label: "Hazardous" },
];

const SOURCE_ICONS = {
  Traffic: "🚗",
  Industry: "🏭",
  Fire: "🔥",
  Dust: "🌫️",
  Mixed: "⚠️",
};

// DOM refs
const citySelect = document.getElementById("citySelect");
const areaSelect = document.getElementById("areaSelect");
const areaLoading = document.getElementById("areaLoading");
const analyzeBtn = document.getElementById("analyzeBtn");
const loadingOverlay = document.getElementById("loadingOverlay");
const loadingText = document.getElementById("loadingText");
const errorBanner = document.getElementById("errorBanner");
const errorText = document.getElementById("errorText");
const dismissError = document.getElementById("dismissError");
const dashboard = document.getElementById("dashboard");

let map = null;
let marker = null;
let cityCoords = {};
let areaCoords = {};
let alertTexts = {};

// ===== Init =====
document.addEventListener("DOMContentLoaded", () => {
  loadCities();

  citySelect.addEventListener("change", loadAreas);
  areaSelect.addEventListener("change", handleAreaChange);
  analyzeBtn.addEventListener("click", runAnalysis);
  dismissError.addEventListener("click", () =>
    errorBanner.classList.add("hidden")
  );

  document.querySelectorAll(".lang-tab").forEach((tab) => {
    tab.addEventListener("click", () => switchLanguage(tab.dataset.lang));
  });
});

// ===== Fetch cities =====
async function loadCities() {
  try {
    let data;
    try {
      data = await fetchJson(`${API_BASE}/api/cities`);
    } catch (err1) {
      if (API_BASE.includes("5050")) {
        try {
          API_BASE = "http://localhost:5000";
          data = await fetchJson(`${API_BASE}/api/cities`);
        } catch (err2) {
          API_BASE = "http://localhost:5050";
          throw err1;
        }
      } else {
        throw err1;
      }
    }
    citySelect.innerHTML = "";

    (data.cities || []).forEach((city) => {
      cityCoords[city.name] = {
        lat: Number(city.lat),
        lon: Number(city.lon),
      };

      const option = document.createElement("option");
      option.value = city.name;
      option.textContent = city.name;
      citySelect.appendChild(option);
    });

    await loadAreas();
  } catch {
    const fallback = [
      "Delhi",
      "Mumbai",
      "Bengaluru",
      "Chennai",
      "Kolkata",
      "Hyderabad",
      "Pune",
      "Ahmedabad",
    ];

    citySelect.innerHTML = "";

    fallback.forEach((name) => {
      const option = document.createElement("option");
      option.value = name;
      option.textContent = name;
      citySelect.appendChild(option);
    });

    showError("Could not load cities from backend. Using default list.");
  }
}

function updateAnalyzeState() {
  analyzeBtn.disabled = !citySelect.value || !areaSelect.value;
}

function setAreaLoading(isLoading) {
  areaLoading.classList.toggle("hidden", !isLoading);
  areaSelect.disabled = isLoading;
}

async function fetchJson(url, timeoutMs = 10000) {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, { signal: controller.signal });
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || `Request failed (${response.status}).`);
    }

    return data;
  } finally {
    clearTimeout(timeoutId);
  }
}

// ===== Fetch areas =====
async function loadAreas() {
  const city = citySelect.value;
  areaCoords = {};
  areaSelect.innerHTML = '<option value="">Loading areas...</option>';
  updateAnalyzeState();

  if (!city) {
    areaSelect.innerHTML = '<option value="">Select a city first</option>';
    areaSelect.disabled = true;
    return;
  }

  setAreaLoading(true);

  try {
    const data = await fetchJson(
      `${API_BASE}/api/areas?city=${encodeURIComponent(city)}`
    );
    console.log("Area API response:", data);

    const areas = Array.isArray(data.areas) ? data.areas : [];
    console.log("Parsed areas:", areas);
    areaSelect.innerHTML = "";

    areas.forEach((area) => {
      areaCoords[area.name] = {
        lat: Number(area.lat),
        lon: Number(area.lon),
      };
      console.log("Stored area coordinates:", area.name, areaCoords[area.name]);

      const option = document.createElement("option");
      option.value = area.name;
      option.textContent = area.name;
      areaSelect.appendChild(option);
    });

    if (areas.length > 0) {
      areaSelect.selectedIndex = 0;
      console.log("Selected area:", areaSelect.value);
      handleAreaChange();
    } else {
      areaSelect.innerHTML = '<option value="">No areas available</option>';
    }
  } catch (err) {
    console.error(err);
    areaSelect.innerHTML = '<option value="">Unable to load areas</option>';
    showError(err.stack || err.message || String(err));
  } finally {
    setAreaLoading(false);
    updateAnalyzeState();
  }
}

function handleAreaChange() {
  const area = areaSelect.value;
  console.log("Selected area:", area);

  if (!area) return;

  const coords = areaCoords[area];
  console.log("Area coordinates lookup:", area, coords);

  if (!coords) {
    console.error("Area not found:", area);
    console.log(areaCoords);
    return;
  }

  moveMapToArea(citySelect.value, area, coords, false);
  updateAnalyzeState();
}

// ===== Analyze =====
async function runAnalysis() {
  const city = citySelect.value;
  const area = areaSelect.value;

  if (!city || !area) return;

  hideError();
  loadingText.textContent = `Analyzing ${area}, ${city}...`;
  loadingOverlay.classList.remove("hidden");
  analyzeBtn.disabled = true;

  try {
    const data = await fetchJson(
      `${API_BASE}/api/analyze?city=${encodeURIComponent(
        city
      )}&area=${encodeURIComponent(area)}`,
      60000
    );

    if (!data.success) {
      throw new Error(data.error || "Analysis failed. Please try again.");
    }

    populateDashboard(data);
    dashboard.classList.remove("hidden");

    initMap();
    map.invalidateSize();
    moveMapToArea(city, area, areaCoords[area], true);
  } catch (err) {
    const message =
      err.name === "AbortError"
        ? "Request timed out after 60 seconds. The backend may still be processing — try again."
        : err.message ||
          "Something went wrong. Is the backend running on port 5000?";

    showError(message);
  } finally {
    loadingOverlay.classList.add("hidden");
    updateAnalyzeState();
  }
}

// ===== Populate dashboard =====
function populateDashboard(data) {
  const aqi = data.aqi_data || {};
  const weather = data.weather || {};
  const traffic = data.traffic || {};
  const ai = data.ai_analysis || {};
  const features = data.features || {};

  animateAqi(aqi.aqi);
  setAqiStyle(aqi.aqi, features.aqi_category || ai.aqi_level);

  document.getElementById("dominantPollutant").textContent =
    aqi.dominant_pollutant || "—";

  document.getElementById("stationName").textContent =
    aqi.station_name || "—";

  document.getElementById("locationName").textContent =
    `${data.city || "—"} · ${data.area || areaSelect.value || "—"}`;

  document.getElementById("sourceIcon").textContent =
    SOURCE_ICONS[ai.primary_source] || "⚠️";

  document.getElementById("primarySource").textContent =
    ai.primary_source || "—";

  setConfidence(ai.primary_confidence);

  document.getElementById("aqiLevel").textContent =
    ai.aqi_level || "—";

  styleBadge(document.getElementById("aqiLevel"), aqi.aqi);

  const secondaryEl = document.getElementById("secondarySources");
  secondaryEl.innerHTML = "";

  (ai.secondary_sources || []).forEach((source) => {
    const badge = document.createElement("span");
    badge.className = "secondary-badge";
    badge.textContent =
      `${SOURCE_ICONS[source.source] || ""} ${source.source}: ${source.confidence}%`;
    secondaryEl.appendChild(badge);
  });

  document.getElementById("reasoning").textContent =
    ai.reasoning || "—";

  document.getElementById("forecastAdvisory").textContent =
    ai.forecast_advisory || "—";

  renderPollutants(aqi);

  document.getElementById("temperature").textContent =
    weather.temperature != null
      ? `${Math.round(weather.temperature)}°C`
      : "—";

  document.getElementById("weatherDesc").textContent =
    weather.description || "—";

  document.getElementById("windSpeed").textContent =
    weather.wind_speed != null
      ? `${weather.wind_speed} km/h`
      : "—";

  document.getElementById("humidity").textContent =
    weather.humidity != null
      ? `${weather.humidity}%`
      : "—";

  document.getElementById("windDir").textContent =
    weather.wind_direction_text || "—";

  if (weather.wind_direction != null) {
    document.getElementById("windArrow").style.transform =
      `rotate(${weather.wind_direction}deg)`;
  }

  setWeatherIcon(weather.description);

  document.getElementById("currentSpeed").textContent =
    traffic.current_speed != null
      ? `${traffic.current_speed} km/h`
      : "—";

  document.getElementById("freeFlowSpeed").textContent =
    traffic.free_flow_speed != null
      ? `${traffic.free_flow_speed} km/h`
      : "—";

  const congestion = traffic.congestion_percent ?? 0;

  document.getElementById("congestionPercent").textContent =
    `${congestion}%`;

  const congestionBar = document.getElementById("congestionBar");
  congestionBar.style.width = `${Math.min(congestion, 100)}%`;
  congestionBar.style.background =
    congestion > 50 ? "#ef4444" :
    congestion > 20 ? "#eab308" :
    "#22c55e";

  const closureEl = document.getElementById("roadClosure");

  if (traffic.road_closure) {
    closureEl.classList.remove("hidden");
  } else {
    closureEl.classList.add("hidden");
  }

  document.getElementById("firesCount").textContent =
    data.fires_count ?? 0;

  document.getElementById("industriesCount").textContent =
    data.nearby_industries ?? 0;

  const fireWarning = document.getElementById("fireWarning");

  if (data.fires_count > 0) {
    fireWarning.classList.remove("hidden");
  } else {
    fireWarning.classList.add("hidden");
  }

  const governmentActions = document.getElementById("govActions");
  governmentActions.innerHTML = "";

  (ai.government_actions || []).forEach((action) => {
    const item = document.createElement("li");
    item.innerHTML = `<i class="fa-solid fa-circle-check"></i> ${action}`;
    governmentActions.appendChild(item);
  });

  alertTexts = {
    english: ai.citizen_alert_english,
    hindi: ai.citizen_alert_hindi,
    telugu: ai.citizen_alert_telugu,
    kannada: ai.citizen_alert_kannada,
  };

  switchLanguage("english");

  document.getElementById("mapCityLabel").textContent =
    `${data.city} · ${data.area || areaSelect.value || "—"}`;
}

// ===== AQI helpers =====
function getAqiLevel(aqi) {
  for (const level of AQI_LEVELS) {
    if (aqi <= level.max) return level;
  }

  return AQI_LEVELS[AQI_LEVELS.length - 1];
}

function setAqiStyle(aqi, categoryLabel) {
  const level = getAqiLevel(aqi ?? 0);
  const number = document.getElementById("aqiNumber");
  const badge = document.getElementById("aqiCategory");

  number.style.color = level.color;
  badge.textContent = categoryLabel || level.label;

  styleBadge(badge, aqi);
}

function styleBadge(element, aqi) {
  const level = getAqiLevel(aqi ?? 0);

  element.style.background = `${level.color}22`;
  element.style.color = level.color;
  element.style.border = `1px solid ${level.color}55`;
}

function animateAqi(target) {
  const element = document.getElementById("aqiNumber");

  if (target == null) {
    element.textContent = "—";
    return;
  }

  const duration = 1200;
  const start = performance.now();

  function step(now) {
    const progress = Math.min((now - start) / duration, 1);
    const eased = 1 - Math.pow(1 - progress, 3);

    element.textContent = Math.round(target * eased);

    if (progress < 1) {
      requestAnimationFrame(step);
    }
  }

  requestAnimationFrame(step);
}

// ===== Confidence ring =====
function setConfidence(percent) {
  const circle = document.getElementById("confidenceCircle");
  const text = document.getElementById("confidenceText");
  const circumference = 2 * Math.PI * 42;

  text.textContent = percent != null ? `${percent}%` : "—%";
  circle.style.strokeDasharray = circumference;
  circle.style.strokeDashoffset =
    percent != null
      ? circumference - (percent / 100) * circumference
      : circumference;
}

// ===== Pollutants =====
function renderPollutants(aqi) {
  const pollutants = [
    { key: "pm25", label: "PM2.5" },
    { key: "pm10", label: "PM10" },
    { key: "no2", label: "NO₂" },
    { key: "so2", label: "SO₂" },
    { key: "co", label: "CO" },
    { key: "o3", label: "O₃" },
  ];

  const grid = document.getElementById("pollutantGrid");
  grid.innerHTML = "";

  pollutants.forEach((pollutant) => {
    const value = aqi[pollutant.key];
    const level = getAqiLevel(value ?? 0);

    const item = document.createElement("div");
    item.className = "pollutant-item";
    item.innerHTML = `
      <div class="label">${pollutant.label}</div>
      <div class="value" style="color:${level.color}">${value ?? "—"}</div>
      <div class="unit">μg/m³</div>`;

    grid.appendChild(item);
  });
}

// ===== Weather icon =====
function setWeatherIcon(description) {
  const icon = document.getElementById("weatherIcon");
  const text = (description || "").toLowerCase();

  if (text.includes("rain")) {
    icon.className = "fa-solid fa-cloud-rain";
  } else if (text.includes("cloud")) {
    icon.className = "fa-solid fa-cloud";
  } else if (text.includes("clear") || text.includes("sun")) {
    icon.className = "fa-solid fa-sun";
  } else if (
    text.includes("mist") ||
    text.includes("fog") ||
    text.includes("haze")
  ) {
    icon.className = "fa-solid fa-smog";
  } else {
    icon.className = "fa-solid fa-cloud-sun";
  }
}

// ===== Language tabs =====
function switchLanguage(language) {
  document.querySelectorAll(".lang-tab").forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.lang === language);
  });

  document.getElementById("alertText").textContent =
    alertTexts[language] || "—";
}

// ===== Map =====
function initMap() {
  if (map) return;

  map = L.map("map", { scrollWheelZoom: false })
    .setView([28.6139, 77.2090], 11);

  L.tileLayer(
    "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>',
      maxZoom: 19,
    }
  ).addTo(map);
}

function moveMapToArea(city, area, coords, openPopup) {
  console.log("Coordinates passed to moveMapToArea:", city, area, coords);
  if (
    !coords ||
    !Number.isFinite(coords.lat) ||
    !Number.isFinite(coords.lon)
  ) {
    console.error("Invalid coordinates:", area, coords);
    return;
  }

  if (!map || dashboard.classList.contains("hidden")) return;

  map.flyTo(
    [coords.lat, coords.lon],
    13,
    { animate: true, duration: 0.7 }
  );

  if (marker) {
    marker.setLatLng([coords.lat, coords.lon]);
  } else {
    marker = L.marker([coords.lat, coords.lon]).addTo(map);
  }

  marker.bindPopup(`<strong>${city}</strong><br>${area}`);

  if (openPopup) {
    marker.openPopup();
  }
}

// ===== Error handling =====
function showError(message) {
  errorText.textContent = message;
  errorBanner.classList.remove("hidden");
}

function hideError() {
  errorBanner.classList.add("hidden");
}
