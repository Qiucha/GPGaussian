/**
 * Phys4DGS Multi-Model Material Segmentation & Trajectory Digest Application
 * Handles Three.js 3D WebGL Point Cloud Rendering, Dual-Mode Frame Player, and Heuristic Inspection
 */

// Application State
let manifest = null;
let currentModelId = "";
let currentStage = 1;
let currentFrame = 0;
let isPlaying = false;
let playTimer = null;
let playbackSpeed = 1.0;

let currentMetadata = null;
let currentPlan = null;
let currentParticles = null;
let currentMetrics = null;

// Three.js 3D Viewport Global References
let scene, camera, renderer, controls, pointCloudGeometry, pointCloudMaterial, pointCloudMesh;
let autoRotate = false;

// Color Palette for Material Tags
const TAG_COLORS = {
  0: "#f43f5e", // Ceramic Red / Base Tag 0
  1: "#f59e0b", // Amber / Woody Stem Tag 1
  2: "#10b981", // Emerald Green / Leaves Foliage Tag 2
  3: "#06b6d4", // Cyan Tag 3
  4: "#8b5cf6", // Purple Tag 4
};

const STAGE_NAMES = {
  1: "1. Raw 3DGS Base Point Cloud",
  2: "2. Spatial Base Cutoff",
  3: "3. Chromatic / SH Filtering",
  4: "4. DBSCAN Noise Filtered",
  5: "5. Final MPM Physics Material Tags",
};

// ----------------------------------------------------
// Initialization
// ----------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  init3DViewport();
  setupEventListeners();
  loadManifest();
});

// ----------------------------------------------------
// Manifest & Data Loading
// ----------------------------------------------------
async function loadManifest() {
  try {
    const response = await fetch("data/manifest.json");
    if (!response.ok) throw new Error("Could not load manifest.json");
    manifest = await response.json();
    populateModelSelector();
  } catch (err) {
    console.error("Error loading manifest:", err);
    const el = document.getElementById("overlay-model-name");
    if (el) el.textContent = "Error loading manifest";
  }
}

function populateModelSelector() {
  const selector = document.getElementById("model-selector");
  if (!selector) return;
  selector.innerHTML = "";

  if (!manifest || !manifest.models || manifest.models.length === 0) return;

  manifest.models.forEach((m) => {
    const opt = document.createElement("option");
    opt.value = m.id;
    opt.textContent = `${m.name} (${m.raw_particles.toLocaleString()} pts)`;
    selector.appendChild(opt);
  });

  currentModelId = manifest.models[0].id;
  loadModelData(currentModelId);
}

async function loadModelData(modelId) {
  try {
    const [metaRes, planRes, partsRes, metricsRes] = await Promise.all([
      fetch(`data/${modelId}/metadata.json`),
      fetch(`data/${modelId}/plan.json`),
      fetch(`data/${modelId}/particles.json`),
      fetch(`data/${modelId}/metrics.json`).catch(() => null),
    ]);

    currentMetadata = await metaRes.json();
    currentPlan = await planRes.json();
    currentParticles = await partsRes.json();
    currentMetrics = metricsRes && metricsRes.ok ? await metricsRes.json() : null;

    // Reset Player to Frame 0
    pausePlayback();
    currentFrame = 0;
    const slider = document.getElementById("frame-slider");
    if (slider) slider.value = 0;
    updateFrameDisplay();

    // Update Reference Render Images
    const refDisplay = document.getElementById("reference-image-display");
    if (refDisplay) refDisplay.src = `data/${modelId}/reference.jpg`;

    const panelRef = document.getElementById("panel-reference-img");
    if (panelRef) panelRef.src = `data/${modelId}/reference.jpg`;

    // Render Panels
    update3DPointCloud();
    renderMetadataPanel();
    renderMetricsPanel();
    renderRefinementHistory();
    renderPhysicsTable();
    renderMaterialBreakdown();
  } catch (err) {
    console.error(`Error loading model data for ${modelId}:`, err);
  }
}

// ----------------------------------------------------
// Panel 1: Three.js 3D WebGL Point Cloud Viewport
// ----------------------------------------------------
function init3DViewport() {
  const container = document.getElementById("three-canvas-container");
  if (!container) return;

  const width = container.clientWidth || 500;
  const height = container.clientHeight || 350;

  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x070a12);

  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 100);
  camera.position.set(0, 1.2, 3.5);

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(width, height, false);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  container.innerHTML = "";
  container.appendChild(renderer.domElement);

  controls = new THREE.OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.05;
  controls.target.set(0, 0.2, 0);

  // ResizeObserver for reliable height/width updates
  const resizeObserver = new ResizeObserver(() => {
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w > 0 && h > 0 && renderer && camera) {
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
  });
  resizeObserver.observe(container);

  animate3D();
}

function animate3D() {
  requestAnimationFrame(animate3D);
  if (autoRotate && controls) {
    controls.update();
    scene.rotation.y += 0.005;
  }
  if (renderer && scene && camera) {
    renderer.render(scene, camera);
  }
}

function update3DPointCloud() {
  if (!currentParticles) return;

  if (pointCloudMesh) {
    scene.remove(pointCloudMesh);
    pointCloudGeometry.dispose();
    pointCloudMaterial.dispose();
  }

  const N = currentParticles.count;
  const positions = new Float32Array(N * 3);
  const colors = new Float32Array(N * 3);

  const pts = currentParticles.positions;
  const rgbColors = currentParticles.colors;
  const stageTags = currentParticles.stages[currentStage.toString()] || currentParticles.tags;

  // Center point cloud
  let cx = 0, cy = 0, cz = 0;
  for (let i = 0; i < N; i++) {
    cx += pts[i][0];
    cy += pts[i][1];
    cz += pts[i][2];
  }
  cx /= N; cy /= N; cz /= N;

  for (let i = 0; i < N; i++) {
    positions[i * 3] = pts[i][0] - cx;
    positions[i * 3 + 1] = pts[i][1] - cy;
    positions[i * 3 + 2] = pts[i][2] - cz;

    if (currentStage === 1) {
      // Raw RGB base colors
      colors[i * 3] = rgbColors[i][0];
      colors[i * 3 + 1] = rgbColors[i][1];
      colors[i * 3 + 2] = rgbColors[i][2];
    } else {
      // Color-coded material tags
      const tag = stageTags[i];
      const hexColor = TAG_COLORS[tag] || "#94a3b8";
      const c = new THREE.Color(hexColor);
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }
  }

  pointCloudGeometry = new THREE.BufferGeometry();
  pointCloudGeometry.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  pointCloudGeometry.setAttribute("color", new THREE.BufferAttribute(colors, 3));

  pointCloudMaterial = new THREE.PointsMaterial({
    size: 0.035,
    vertexColors: true,
    transparent: true,
    opacity: 0.9,
  });

  pointCloudMesh = new THREE.Points(pointCloudGeometry, pointCloudMaterial);
  scene.add(pointCloudMesh);

  // Update Overlays
  const elModel = document.getElementById("overlay-model-name");
  if (elModel) elModel.textContent = currentModelId;
  const elStage = document.getElementById("overlay-stage-name");
  if (elStage) elStage.textContent = STAGE_NAMES[currentStage];
  const elCount = document.getElementById("overlay-particle-count");
  if (elCount) elCount.textContent = `${currentParticles.count.toLocaleString()} WebGL Points`;

  renderViewportLegend();
}

function renderViewportLegend() {
  const legendBox = document.getElementById("viewport-legend");
  if (!legendBox) return;
  legendBox.innerHTML = "";

  if (currentStage === 1) {
    legendBox.innerHTML = `
      <div class="legend-item">
        <span class="legend-dot" style="background:#3b82f6;"></span>
        <span>Raw 0th-Order SH Base Colors</span>
      </div>`;
    return;
  }

  if (!currentPlan || !currentPlan.materials) return;

  currentPlan.materials.forEach((mat) => {
    const col = TAG_COLORS[mat.tag_id] || "#94a3b8";
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="legend-dot" style="background:${col};"></span>
      <span>Tag ${mat.tag_id}: ${mat.name}</span>`;
    legendBox.appendChild(item);
  });
}

// ----------------------------------------------------
// Panel 2: Frame-by-Frame Trajectory Player
// ----------------------------------------------------
function updateFrameDisplay() {
  const imgEl = document.getElementById("frame-image");
  if (!imgEl) return;
  const padFrame = String(currentFrame).padStart(2, "0");
  imgEl.src = `data/${currentModelId}/frames/frame_${padFrame}.jpg`;

  const fc = document.getElementById("frame-counter");
  if (fc) fc.textContent = `Frame ${padFrame} / 29`;
  const tc = document.getElementById("time-counter");
  if (tc) {
    const t_sec = (currentFrame / 29) * 0.4;
    tc.textContent = `t = ${t_sec.toFixed(3)}s`;
  }
}

function startPlayback() {
  if (isPlaying) return;
  isPlaying = true;
  const btn = document.getElementById("play-pause-icon");
  if (btn) btn.className = "fa-solid fa-pause";

  const intervalMs = Math.round(100 / playbackSpeed);
  playTimer = setInterval(() => {
    currentFrame = (currentFrame + 1) % 30;
    const slider = document.getElementById("frame-slider");
    if (slider) slider.value = currentFrame;
    updateFrameDisplay();
  }, intervalMs);
}

function pausePlayback() {
  isPlaying = false;
  const btn = document.getElementById("play-pause-icon");
  if (btn) btn.className = "fa-solid fa-play";
  if (playTimer) {
    clearInterval(playTimer);
    playTimer = null;
  }
}

function togglePlayback() {
  if (isPlaying) pausePlayback();
  else startPlayback();
}

// ----------------------------------------------------
// Panel 3: LLM Heuristic Choice & Rationale Inspector
// ----------------------------------------------------
function renderMetadataPanel() {
  if (!currentMetadata) return;

  const metaBox = document.getElementById("metadata-box");
  if (metaBox) {
    metaBox.textContent = `Scene: ${currentModelId}
Extents: X=[${currentMetadata.min_xyz[0].toFixed(2)}, ${currentMetadata.max_xyz[0].toFixed(2)}], Y=[${currentMetadata.min_xyz[1].toFixed(2)}, ${currentMetadata.max_xyz[1].toFixed(2)}], Z=[${currentMetadata.min_xyz[2].toFixed(2)}, ${currentMetadata.max_xyz[2].toFixed(2)}]
Y-Percentiles: p25=${currentMetadata.y_percentiles.p25.toFixed(2)}, p50=${currentMetadata.y_percentiles.p50.toFixed(2)}, p75=${currentMetadata.y_percentiles.p75.toFixed(2)}
Color Dominance: Red=${currentMetadata.color_dominance_pct.red_dominant.toFixed(1)}%, Green=${currentMetadata.color_dominance_pct.green_dominant.toFixed(1)}%, Blue=${currentMetadata.color_dominance_pct.blue_dominant.toFixed(1)}%
Gaussian Anisotropy Ratio: Mean=${currentMetadata.mean_anisotropy_ratio.toFixed(2)}, Highly Anisotropic (>3x): ${currentMetadata.pct_anisotropic.toFixed(1)}%`;
  }

  const stepsList = document.getElementById("heuristics-list");
  if (!stepsList) return;
  stepsList.innerHTML = "";

  if (!currentPlan || !currentPlan.steps) return;

  currentPlan.steps.forEach((step, idx) => {
    const card = document.createElement("div");
    card.className = "step-card";
    const paramsStr = JSON.stringify(step.params);
    card.innerHTML = `
      <div class="step-card-header">
        <span class="step-name">Step ${idx + 1}: ${step.primitive_type}</span>
        <span class="step-tag">${paramsStr}</span>
      </div>
      <div class="step-desc">${step.description}</div>`;
    stepsList.appendChild(card);
  });
}

// ----------------------------------------------------
// Panel 3 (Continued): Quantitative Metrics & Refinement History
// ----------------------------------------------------
function renderMetricsPanel() {
  const badgeEl = document.getElementById("metric-quality-badge");
  const silEl = document.getElementById("metric-silhouette");
  const speckleEl = document.getElementById("metric-speckle");
  const turnsEl = document.getElementById("metric-refinement-turns");

  if (!currentMetrics) {
    if (badgeEl) { badgeEl.className = "badge badge-quality rating-good"; badgeEl.textContent = "GOOD"; }
    if (silEl) silEl.textContent = "N/A";
    if (speckleEl) speckleEl.textContent = "N/A";
    if (turnsEl) turnsEl.textContent = "1 Iteration";
  } else {
    const rating = currentMetrics.overall_quality_rating || "GOOD";
    const ratingClass = `rating-${rating.toLowerCase()}`;
    if (badgeEl) {
      badgeEl.className = `badge badge-quality ${ratingClass}`;
      badgeEl.textContent = rating.replace("_", " ");
    }
    if (silEl) silEl.textContent = (currentMetrics.silhouette_score || 0).toFixed(3);
    if (speckleEl) speckleEl.textContent = `${(currentMetrics.speckle_total_pct || 0).toFixed(1)}%`;
    if (turnsEl) turnsEl.textContent = `${currentMetrics.refinement_iterations || 1} Iterations`;
  }

  // Render per-tag details table
  const box = document.getElementById("metrics-breakdown-box");
  if (!box) return;
  box.innerHTML = "";

  if (!currentMetrics || !currentMetrics.tag_metrics) {
    box.innerHTML = `<p style="font-size:12px; color:var(--text-muted);">No quantitative metrics available.</p>`;
    return;
  }

  let html = `<table class="metrics-subtable">
    <thead>
      <tr>
        <th>Tag / Material</th>
        <th>Particles</th>
        <th>Speckle Noise</th>
        <th>Components</th>
      </tr>
    </thead>
    <tbody>`;

  currentMetrics.tag_metrics.forEach((tm) => {
    html += `<tr>
      <td>Tag ${tm.tag_id} (${tm.name})</td>
      <td>${tm.particle_count.toLocaleString()} (${tm.percentage.toFixed(1)}%)</td>
      <td>${tm.speckle_count} (${tm.speckle_percentage.toFixed(1)}%)</td>
      <td>${tm.connected_components}</td>
    </tr>`;
  });

  html += `</tbody></table>`;
  box.innerHTML = html;
}

function renderRefinementHistory() {
  const box = document.getElementById("refinement-history-box");
  if (!box) return;
  box.innerHTML = "";

  if (!currentMetrics || !currentMetrics.refinement_history || currentMetrics.refinement_history.length === 0) {
    box.innerHTML = `<p style="font-size:12px; color:var(--text-muted);">No refinement history recorded.</p>`;
    return;
  }

  currentMetrics.refinement_history.forEach((turn) => {
    const card = document.createElement("div");
    card.className = "refinement-turn-card";

    const turnMetrics = turn.metrics || {};
    const turnRating = turnMetrics.overall_quality_rating || "GOOD";
    const sil = turnMetrics.silhouette_score != null ? turnMetrics.silhouette_score.toFixed(3) : "N/A";
    const speckle = turnMetrics.speckle_total_pct != null ? `${turnMetrics.speckle_total_pct.toFixed(1)}%` : "N/A";

    let stepsHtml = "";
    if (turn.plan && turn.plan.steps) {
      turn.plan.steps.forEach((s) => {
        stepsHtml += `<div class="turn-step-chip"><strong>${s.primitive_type}</strong>: ${s.description}</div>`;
      });
    }

    card.innerHTML = `
      <div class="turn-header">
        <span class="turn-title"><i class="fa-solid fa-turn-up"></i> Iteration ${turn.iteration}</span>
        <span class="turn-metrics">Rating: ${turnRating} | Silhouette: ${sil} | Speckle: ${speckle}</span>
      </div>
      <div class="turn-steps">${stepsHtml}</div>`;
    box.appendChild(card);
  });
}

// ----------------------------------------------------
// Panel 4: Physical Properties Matrix ($E, \nu, \rho, \mu, \lambda$)
// ----------------------------------------------------
function renderPhysicsTable() {
  const tbody = document.getElementById("physics-table-body");
  if (!tbody) return;
  tbody.innerHTML = "";

  if (!currentPlan || !currentPlan.materials) return;

  currentPlan.materials.forEach((mat) => {
    const E = mat.E;
    const nu = mat.nu;
    const rho = mat.density;

    // Lamé shear modulus mu = E / (2*(1+nu))
    const mu = E / (2.0 * (1.0 + nu));
    // Lamé bulk modulus lambda = (E*nu) / ((1+nu)*(1-2*nu))
    const lambda = (E * nu) / ((1.0 + nu) * (1.0 - 2.0 * nu));

    const row = document.createElement("tr");
    row.innerHTML = `
      <td><strong>Tag ${mat.tag_id} (${mat.name})</strong></td>
      <td>${E.toExponential(1)}</td>
      <td>${nu.toFixed(2)}</td>
      <td>${rho.toFixed(0)}</td>
      <td>${mu.toExponential(2)}</td>
      <td>${lambda.toExponential(2)}</td>`;
    tbody.appendChild(row);
  });
}

// ----------------------------------------------------
// Panel 5: Material Tag Distribution Breakdown
// ----------------------------------------------------
function renderMaterialBreakdown() {
  const container = document.getElementById("material-breakdown-list");
  if (!container) return;
  container.innerHTML = "";

  if (!currentParticles || !currentPlan || !currentPlan.materials) return;

  const N = currentParticles.count;
  const tags = currentParticles.stages[currentStage.toString()] || currentParticles.tags;

  // Compute tag frequency
  const tagCounts = {};
  tags.forEach((t) => {
    tagCounts[t] = (tagCounts[t] || 0) + 1;
  });

  currentPlan.materials.forEach((mat) => {
    const count = tagCounts[mat.tag_id] || 0;
    const pct = ((count / N) * 100).toFixed(1);
    const col = TAG_COLORS[mat.tag_id] || "#94a3b8";

    const item = document.createElement("div");
    item.className = "breakdown-item";
    item.innerHTML = `
      <div class="breakdown-info">
        <span>Tag ${mat.tag_id}: ${mat.name}</span>
        <span>${count.toLocaleString()} pts (${pct}%)</span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" style="width: ${pct}%; background: ${col};"></div>
      </div>`;
    container.appendChild(item);
  });
}

// ----------------------------------------------------
// UI Event Handlers
// ----------------------------------------------------
function setupEventListeners() {
  // Model Selector
  const modelSelect = document.getElementById("model-selector");
  if (modelSelect) {
    modelSelect.addEventListener("change", (e) => {
      currentModelId = e.target.value;
      loadModelData(currentModelId);
    });
  }

  // Pipeline Stage Tabs
  const stageContainer = document.getElementById("stage-tabs-container");
  if (stageContainer) {
    stageContainer.addEventListener("click", (e) => {
      const tab = e.target.closest(".stage-tab");
      if (!tab) return;

      document.querySelectorAll(".stage-tab").forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      currentStage = parseInt(tab.dataset.stage, 10);
      update3DPointCloud();
      renderMaterialBreakdown();
    });
  }

  // Reference Image Overlay Toggle
  const btnToggleRef = document.getElementById("btn-toggle-ref");
  const btnCloseRef = document.getElementById("btn-close-ref");
  const refOverlay = document.getElementById("reference-image-overlay");

  if (btnToggleRef && refOverlay) {
    btnToggleRef.addEventListener("click", () => {
      refOverlay.classList.toggle("hidden");
    });
  }
  if (btnCloseRef && refOverlay) {
    btnCloseRef.addEventListener("click", () => {
      refOverlay.classList.add("hidden");
    });
  }

  // 3D Controls
  const btnReset = document.getElementById("btn-reset-cam");
  if (btnReset) {
    btnReset.addEventListener("click", () => {
      camera.position.set(0, 1.2, 3.5);
      controls.target.set(0, 0.2, 0);
      scene.rotation.y = 0;
    });
  }

  const btnRotate = document.getElementById("btn-toggle-rotate");
  if (btnRotate) {
    btnRotate.addEventListener("click", () => {
      autoRotate = !autoRotate;
      btnRotate.classList.toggle("btn-primary", autoRotate);
    });
  }

  // Frame Player Controls
  const btnPlay = document.getElementById("btn-play-pause");
  if (btnPlay) btnPlay.addEventListener("click", togglePlayback);

  const btnFirst = document.getElementById("btn-first-frame");
  if (btnFirst) {
    btnFirst.addEventListener("click", () => {
      pausePlayback();
      currentFrame = 0;
      const slider = document.getElementById("frame-slider");
      if (slider) slider.value = 0;
      updateFrameDisplay();
    });
  }

  const btnLast = document.getElementById("btn-last-frame");
  if (btnLast) {
    btnLast.addEventListener("click", () => {
      pausePlayback();
      currentFrame = 29;
      const slider = document.getElementById("frame-slider");
      if (slider) slider.value = 29;
      updateFrameDisplay();
    });
  }

  const btnPrev = document.getElementById("btn-prev-frame");
  if (btnPrev) {
    btnPrev.addEventListener("click", () => {
      pausePlayback();
      currentFrame = (currentFrame - 1 + 30) % 30;
      const slider = document.getElementById("frame-slider");
      if (slider) slider.value = currentFrame;
      updateFrameDisplay();
    });
  }

  const btnNext = document.getElementById("btn-next-frame");
  if (btnNext) {
    btnNext.addEventListener("click", () => {
      pausePlayback();
      currentFrame = (currentFrame + 1) % 30;
      const slider = document.getElementById("frame-slider");
      if (slider) slider.value = currentFrame;
      updateFrameDisplay();
    });
  }

  const slider = document.getElementById("frame-slider");
  if (slider) {
    slider.addEventListener("input", (e) => {
      pausePlayback();
      currentFrame = parseInt(e.target.value, 10);
      updateFrameDisplay();
    });
  }

  const speedSelect = document.getElementById("speed-select");
  if (speedSelect) {
    speedSelect.addEventListener("change", (e) => {
      playbackSpeed = parseFloat(e.target.value);
      if (isPlaying) {
        pausePlayback();
        startPlayback();
      }
    });
  }
}
