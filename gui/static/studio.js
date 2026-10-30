/* 本地照片工作台：界面参数进入真实单头运行库，异步结果按请求身份更新。 */
(() => {
  "use strict";
  const $ = id => document.getElementById(id);
  const token = document.querySelector('meta[name="app-token"]').content;
  const ui = { catalog: null, photo: null, preset: null, stages: [], profile: "balanced", weights: [.7, .5, .3], threads: 4,
    mode: "compare", photoFilter: "全部", lookFilter: "全部", result: null, busy: false, dirty: false,
    request: 0, thumbVersion: 0, zoom: 1, pan: [0, 0], holdingOriginal: false };
  let controller, renderTimer, toastTimer;
  const svg = name => { const icon = document.createElementNS("http://www.w3.org/2000/svg", "svg"); icon.classList.add("icon"); icon.setAttribute("aria-hidden", "true"); const use = document.createElementNS(icon.namespaceURI, "use"); use.setAttribute("href", "#i-" + name); icon.append(use); return icon; };
  const el = (tag, className, value) => { const node = document.createElement(tag); if (className) node.className = className; if (value !== undefined) node.textContent = value; return node; };
  const text = (id, value) => { $(id).textContent = value; };
  const clone = value => JSON.parse(JSON.stringify(value));
  const number = (value, digits = 2) => Number.isFinite(Number(value)) && value !== null ? new Intl.NumberFormat("zh-CN", { maximumFractionDigits: digits, minimumFractionDigits: digits }).format(Number(value)) : "—";
  const bytes = value => Number.isFinite(Number(value)) ? value >= 1048576 ? `${number(value / 1048576, 2)} MiB` : `${number(value / 1024, 1)} KiB` : "—";
  const photoUrl = (id, size = "preview") => `/api/studio/photo?${new URLSearchParams({ id, size })}`;
  const native = () => Boolean(ui.preset?.native_profile);
  const custom = () => !native() && ui.stages.some((stage, index) => ["lut", "enabled", "strength"].some(key => stage[key] !== ui.preset.stages[index][key]));

  async function api(path, data, signal) {
    const response = await fetch(path, data === undefined ? { signal } : { method: "POST", signal, headers: { "Content-Type": "application/json", "X-App-Token": token }, body: JSON.stringify(data) });
    const value = await response.json().catch(() => ({ message: "本地服务返回了无法读取的响应" }));
    if (!response.ok) throw new Error(value.message || `请求失败（${response.status}）`);
    return value;
  }

  function toast(message, error = false) {
    clearTimeout(toastTimer); const node = $("toast"); node.textContent = message; node.classList.toggle("error", error); node.hidden = false;
    toastTimer = setTimeout(() => { node.hidden = true; }, error ? 6000 : 3000);
  }

  function setBusy(value, message = "四级 LUT 正在处理") {
    ui.busy = value; $("viewer").setAttribute("aria-busy", String(value)); $("loading-overlay").hidden = !value;
    text("loading-text", message); $("export-button").disabled = value || ui.dirty || !ui.result;
    if (value) { text("render-status", "正在计算预览"); text("measurement-check", "计算中"); }
  }

  function renderEngine(engine) {
    const ready = engine?.available === true;
    text("engine-label", ready ? `${(engine.backend || "CPU").toUpperCase()} · 本地引擎` : "引擎未就绪");
    $("engine-pill").classList.toggle("failed", !ready); $("connection-dot").style.background = ready ? "var(--green)" : "var(--red)";
    text("connection-status", ready ? "本地连接正常" : "请检查运行库"); text("footer-backend", ready ? `${String(engine.backend || "CPU").toUpperCase()} / C++17` : "CPU");
    text("about-engine", engine?.name || "当前引擎未就绪"); text("about-backend", String(engine?.backend || "—").toUpperCase()); text("about-sha", engine?.library_sha256 || engine?.error || "—");
  }

  function photoCategories() { return ["全部", ...new Set(ui.catalog.photos.map(photo => photo.category).filter(Boolean))]; }
  function renderPhotoFilters() {
    const parent = $("photo-filters"); parent.replaceChildren();
    for (const category of photoCategories()) { const button = el("button", category === ui.photoFilter ? "active" : "", category); button.setAttribute("aria-pressed", String(category === ui.photoFilter)); button.onclick = () => { ui.photoFilter = category; renderPhotoFilters(); renderPhotos(); }; parent.append(button); }
  }
  function renderPhotos() {
    const parent = $("photo-grid"), query = $("photo-search").value.trim().toLowerCase(); parent.replaceChildren();
    const photos = ui.catalog.photos.filter(photo => (ui.photoFilter === "全部" || photo.category === ui.photoFilter) && [photo.title, photo.description, ...(photo.tags || [])].join(" ").toLowerCase().includes(query));
    text("photo-count", `${photos.length} / ${ui.catalog.photos.length}`);
    for (const photo of photos) {
      const button = el("button", "photo-tile" + (ui.photo?.id === photo.id ? " active" : "")); button.title = photo.description || photo.title; button.setAttribute("aria-label", `选择样片：${photo.title}`); button.setAttribute("aria-pressed", String(ui.photo?.id === photo.id));
      const wrapper = el("div", "thumb-wrap"), img = el("img"); img.src = photoUrl(photo.id, "thumb"); img.alt = photo.title; img.loading = "lazy";
      const check = el("span", "photo-check"); check.append(svg("check")); wrapper.append(img, check); button.append(wrapper, el("strong", "", photo.title), el("small", "", photo.category)); button.onclick = () => choosePhoto(photo.id); parent.append(button);
    }
    if (!photos.length) parent.append(el("p", "no-photos", "没有匹配的样片，试试其他关键词。"));
  }

  function choosePhoto(id) {
    const photo = ui.catalog.photos.find(item => item.id === id); if (!photo || ui.photo?.id === id) return;
    ui.photo = photo; ui.result = null; ui.zoom = 1; ui.pan = [0, 0]; applyZoom();
    $("original-image").src = photoUrl(id); $("original-image").alt = photo.title + " · 原始照片"; $("output-image").removeAttribute("src"); $("difference-image").removeAttribute("src");
    text("photo-title", photo.title); text("photo-size", "RGB8"); text("footer-photo", [photo.title, photo.category, (photo.tags || []).slice(0, 2).join(" / ")].filter(Boolean).join(" · "));
    updateSource(); renderPhotos(); queueLookThumbnails(); scheduleRender(0);
  }

  function lookCategories() { return ["全部", ...new Set(ui.catalog.presets.map(item => item.category).filter(Boolean))]; }
  function renderLooks() {
    const filters = $("looks-filters"), filterScroll = filters.scrollLeft; filters.replaceChildren();
    for (const category of lookCategories()) { const button = el("button", category === ui.lookFilter ? "active" : "", category); button.setAttribute("aria-pressed", String(category === ui.lookFilter)); button.onclick = () => { ui.lookFilter = category; renderLooks(); }; filters.append(button); }
    filters.scrollLeft = filterScroll;
    text("looks-count", `${ui.catalog.presets.length} 种组合`);
    const parent = $("looks-grid"); parent.replaceChildren();
    for (const preset of ui.catalog.presets.filter(item => ui.lookFilter === "全部" || item.category === ui.lookFilter)) {
      const button = el("button", "look-card pending" + (ui.preset?.id === preset.id ? " active" : "")); button.dataset.preset = preset.id; button.setAttribute("aria-label", `应用组合：${preset.title}`); button.setAttribute("aria-pressed", String(ui.preset?.id === preset.id)); button.title = preset.description;
      const wrapper = el("div", "look-image"); const colours = Array.isArray(preset.swatch) ? preset.swatch.filter(value => /^#[0-9a-f]{6}$/i.test(value)) : [];
      if (colours.length) wrapper.style.background = `linear-gradient(120deg,${colours.join(",")})`;
      const img = el("img"); img.hidden = true; img.alt = preset.title + " · 实际风格预览";
      const check = el("span", "look-selected"); check.append(svg("check")); wrapper.append(img, check);
      if (preset.native_profile) wrapper.append(el("span", "native-marker", "CINEMA MODEL"));
      const title = el("div"); title.append(el("strong", "", preset.title), el("small", "", preset.category || "LOOK")); button.append(wrapper, title); button.onclick = () => choosePreset(preset.id); parent.append(button);
    }
    queueLookThumbnails();
  }

  function queueLookThumbnails() {
    if (!ui.photo) return;
    const version = ++ui.thumbVersion, photo = ui.photo.id, cards = [...$("looks-grid").querySelectorAll(".look-card")]; let cursor = 0;
    async function worker() {
      while (cursor < cards.length && version === ui.thumbVersion) {
        const card = cards[cursor++], img = card.querySelector("img"), preset = card.dataset.preset;
        const url = `/api/studio/look?${new URLSearchParams({ photo, preset })}`;
        try {
          await new Promise((resolve, reject) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = reject; image.src = url; });
          if (version !== ui.thumbVersion) return; img.src = url; img.hidden = false; card.classList.remove("pending");
        } catch (_) { if (version === ui.thumbVersion) { img.removeAttribute("src"); img.hidden = true; card.title = "预览暂不可用，点击组合查看完整结果"; card.classList.remove("pending"); } }
      }
    }
    // 留出首幅大图请求，随后每次仅计算两个实际风格缩略图。
    setTimeout(() => { if (version === ui.thumbVersion) { worker(); worker(); } }, 180);
  }

  function choosePreset(id) {
    const preset = ui.catalog.presets.find(item => item.id === id); if (!preset) return;
    ui.preset = preset; ui.stages = clone(preset.stages); ui.dirty = false; ui.result = null;
    text("selected-look-title", preset.title); text("selected-look-description", preset.description || "四级顺序处理，调整每一级探索不同色彩。"); text("look-tag", preset.native_profile ? "固定模型" : "可编辑组合");
    text("result-look-label", preset.title); text("chain-note", native() ? "当前为固定Cinema模型。切换创意组合后，可逐级调整LUT与强度。" : "调整任一级LUT或强度后，预览会自动更新。");
    for (const card of $("looks-grid").querySelectorAll(".look-card")) { const selected = card.dataset.preset === id; card.classList.toggle("active", selected); card.setAttribute("aria-pressed", String(selected)); }
    renderStages(); scheduleRender(0);
  }

  function renderStages() {
    const list = $("stage-list"); list.replaceChildren();
    ui.stages.forEach((stage, index) => {
      const fixed = native(), card = el("div", "stage-card" + (stage.enabled === false && !fixed ? " disabled" : "") + (fixed ? " native" : ""));
      const heading = el("div", "stage-head"); heading.append(el("span", "stage-number", String(index + 1).padStart(2, "0")), el("strong", "", `第${["一", "二", "三", "四"][index]}级 LUT`));
      if (fixed) heading.append(el("small", "", "固定模型"));
      else { const toggle = el("button", "stage-toggle"); toggle.setAttribute("aria-pressed", String(stage.enabled !== false)); toggle.setAttribute("aria-label", `启用第${index + 1}级LUT`); toggle.append(el("span")); toggle.onclick = () => { stage.enabled = stage.enabled === false; markEdited(); renderStages(); }; heading.append(toggle); }
      const select = el("select", "lut-select"); select.setAttribute("aria-label", `第${index + 1}级LUT素材`);
      if (fixed) { const actual = ui.result?.stages?.[index]; select.append(new Option(actual?.display_title || `Cinema · Stage ${index + 1}`, "fixed")); select.disabled = true; }
      else { select.append(new Option("保持原色 · Identity", "identity")); for (const lut of ui.catalog.luts) select.append(new Option(lut.title, lut.id)); select.value = stage.lut; select.onchange = () => { stage.lut = select.value; if (stage.lut === "identity") { stage.strength = 0; stage.enabled = false; } else { stage.enabled = true; if (!stage.strength) stage.strength = .25; } markEdited(); renderStages(); }; }
      card.append(heading, select);
      if (fixed) { const actual = ui.result?.stages?.[index]; card.append(el("p", "native-stage-info", actual?.m ? `m${actual.m} · Q16 四面体 · 只读模型` : "四级整数模型 · 原始sidecar保留")); }
      else {
        const strength = el("div", "stage-strength"), label = el("label", "strength-heading"), range = el("input"), output = el("output");
        range.type = "range"; range.id = `stage-strength-${index}`; range.min = 0; range.max = 100; range.value = Math.round((stage.strength ?? 1) * 100); range.disabled = stage.lut === "identity"; range.setAttribute("aria-label", `第${index + 1}级强度`); label.htmlFor = range.id;
        output.textContent = range.value + "%"; label.append(el("span", "", "混合强度"), output);
        range.oninput = () => { stage.strength = Number(range.value) / 100; output.textContent = range.value + "%"; invalidate(); };
        range.onchange = () => markEdited(); strength.append(label, range); card.append(strength);
      }
      list.append(card);
    });
  }

  function invalidate() { controller?.abort(); ++ui.request; ui.dirty = true; $("export-button").disabled = true; }
  function markEdited() { text("look-tag", native() ? "固定模型 · 参数" : "自定义调整"); text("render-status", "参数已更新"); scheduleRender(); }
  function scheduleRender(delay = 240) { clearTimeout(renderTimer); invalidate(); if (ui.photo && ui.preset) renderTimer = setTimeout(render, delay); }
  function loadImage(url) { return new Promise((resolve, reject) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = () => reject(new Error("处理完成，但结果图片读取失败，请重试。")); image.src = url; }); }

  async function render() {
    if (!ui.photo || !ui.preset) return;
    if (!ui.weights.some(value => value > 0)) { setBusy(false); $("export-button").disabled = true; text("render-status", "请设置至少一项偏好"); toast("三个偏好不能全部为0，请保留至少一项。", true); return; }
    controller?.abort(); controller = new AbortController(); const request = ++ui.request;
    $("viewer-empty").hidden = true; setBusy(true); const data = { photo: ui.photo.id, preset: ui.preset.id, profile: ui.profile, weights: ui.weights, threads: ui.threads };
    if (!native()) data.stages = clone(ui.stages);
    try {
      const result = await api("/api/studio/render", data, controller.signal);
      await loadImage(result.image_url); if (request !== ui.request) return;
      ui.result = result; ui.dirty = false; $("output-image").src = result.image_url; $("output-image").alt = `${ui.photo.title} · ${ui.preset.title}处理结果`;
      if (result.difference_url) $("difference-image").src = result.difference_url;
      const width = result.width, height = result.height; if (width && height) text("photo-size", `${width} × ${height} · RGB8`);
      renderMetrics(result); if (native()) renderStages(); applyMode(); setBusy(false);
    } catch (error) {
      if (error.name === "AbortError" || request !== ui.request) return;
      setBusy(false); $("export-button").disabled = true; $("viewer-empty").hidden = false; text("viewer-error", error.message); text("render-status", "处理失败，可重试"); text("measurement-check", "未完成"); toast(error.message, true);
    }
  }

  function renderMetrics(result) {
    const m = result.metrics || {}, config = result.config || {};
    const time = $("metric-time"); time.replaceChildren(document.createTextNode(number(m.apply_ms, 3)), el("small", "", "ms"));
    text("metric-error", number(m.mean_delta_e, 3)); text("metric-max", number(m.max_delta_e, 3)); text("metric-model", bytes(m.model_bytes));
    text("measurement-check", m.runtime_equal === true ? "✓ 同模型字节核对一致" : m.runtime_equal === false ? "字节核对未通过" : "实际处理结果");
    $("measurement-check").style.color = m.runtime_equal === false ? "var(--red)" : "";
    const mValues = Array.isArray(config.m) ? config.m : [];
    text("actual-grid", mValues.length ? mValues.map(value => "m" + value).join(" / ") : "—");
    const backend = String(config.backend || "CPU").toUpperCase(), representation = { sparse: "稀疏表", direct_u8: "U8 direct", direct_u16: "U16 direct", direct_rgb24: "RGB24 direct" }[config.representation] || config.representation;
    text("actual-backend", [backend, representation].filter(Boolean).join(" · ")); text("actual-arena", bytes(m.arena_bytes));
    text("selection-policy", config.selection_policy || "参数驱动实际配置，本图实时计算。");
    text("measurement-scope", m.mean_delta_e === null ? "当前无密集源参考，色差未提供；仍核对本图C++/C99输出。" : "本图相对源LUT参考的RGB代码距离；耗时仅映射，模型/工作区按实际容量记账。");
    $("metric-info").title = `${m.reference_kind || config.quality_scope || "当前图像的源LUT参考"}。RGB代码欧氏距离，非CIEDE2000。`;
    text("render-status", "预览已更新"); text("render-config", `${backend} · ${config.threads || ui.threads}T · ${mValues.length ? "m" + mValues[0] : "Q16"} / ${number(m.apply_ms, 2)} ms${m.mean_delta_e === null ? "" : " / ΔE " + number(m.mean_delta_e, 3)}`);
    text("result-look-label", ui.preset.title + (custom() ? " · 自定义" : ""));
    text("look-tag", native() ? "固定模型" : custom() ? "自定义调整" : "可编辑组合");
    const differenceScope = m.difference_scope || "实际差异图，请查看参考口径";
    $("difference-image").alt = differenceScope;
    document.querySelector('button[data-mode="difference"]').title = differenceScope;
    if (result.engine) renderEngine(result.engine);
  }

  function applyMode() {
    const mode = ui.holdingOriginal ? "original" : ui.mode; $("viewer").dataset.mode = mode;
    $("difference-image").hidden = mode !== "difference"; $("processed-layer").hidden = !ui.result;
    for (const button of document.querySelectorAll("[data-mode]")) { if (button.tagName !== "BUTTON") continue; const selected = button.dataset.mode === ui.mode; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); }
    if (mode === "difference") { const scope = ui.result?.metrics?.difference_scope || "处理与参考的实际差异"; text("result-look-label", scope); $("after-label").title = scope; } else if (ui.preset) { text("result-look-label", ui.preset.title + (ui.dirty ? " · 正在调整" : custom() ? " · 自定义" : "")); $("after-label").title = ""; }
    text("viewer-hint", ""); $("viewer-hint").append(el("kbd", "", "空格"), document.createTextNode("按住查看原图"));
  }

  function applyZoom() {
    $("viewer").style.setProperty("--zoom", String(ui.zoom)); $("viewer").style.setProperty("--pan-x", ui.pan[0] + "px"); $("viewer").style.setProperty("--pan-y", ui.pan[1] + "px");
    $("viewer").classList.toggle("zoomed", ui.zoom > 1); text("zoom-fit", ui.zoom === 1 ? "适应画面" : `${Math.round(ui.zoom * 100)}%`);
  }
  function setZoom(value) { ui.zoom = Math.max(1, Math.min(3, value)); if (ui.zoom === 1) ui.pan = [0, 0]; applyZoom(); }
  function updatePreferenceLabels() { ["accuracy", "speed", "memory"].forEach((key, index) => { $("weight-" + key).value = Math.round(ui.weights[index] * 100); text("weight-" + key + "-value", Math.round(ui.weights[index] * 100)); }); }

  function updateSource() {
    if (!ui.photo) return; const source = ui.photo.source, sourceName = typeof source === "string" ? source : source?.dataset || source?.title || source?.name || "项目摄影素材";
    text("about-current-source", `当前样片：${ui.photo.title} / ${sourceName} / ${ui.photo.license || "保留原来源使用限制"}`);
  }
  function about() { updateSource(); if (!$("about-dialog").open) $("about-dialog").showModal(); }
  function reset() { if (!ui.preset) return; ui.stages = clone(ui.preset.stages); ui.dirty = false; text("look-tag", native() ? "固定模型" : "可编辑组合"); renderStages(); scheduleRender(0); toast("已还原当前组合的四级LUT与强度。"); }

  document.querySelectorAll("[data-mode]").forEach(button => { if (button.tagName === "BUTTON") button.onclick = () => { ui.mode = button.dataset.mode; applyMode(); }; });
  document.querySelectorAll("[data-panel]").forEach(button => button.onclick = () => { for (const name of ["chain", "performance"]) { const active = button.dataset.panel === name; $("tab-" + name).classList.toggle("active", active); $("tab-" + name).setAttribute("aria-selected", String(active)); $("panel-" + name).hidden = !active; } });
  document.querySelectorAll("[data-profile]").forEach(button => button.onclick = () => { ui.profile = button.dataset.profile; ui.weights = { balanced: [.7, .5, .3], detail: [.95, .35, .15], compact: [.3, .6, .95] }[ui.profile]; updatePreferenceLabels(); for (const item of document.querySelectorAll("[data-profile]")) item.classList.toggle("active", item === button); markEdited(); });
  ["accuracy", "speed", "memory"].forEach((key, index) => { $("weight-" + key).oninput = event => { ui.weights[index] = Number(event.target.value) / 100; text("weight-" + key + "-value", event.target.value); invalidate(); }; $("weight-" + key).onchange = () => markEdited(); });
  $("thread-select").onchange = event => { ui.threads = Number(event.target.value); markEdited(); };
  $("photo-search").oninput = () => { if (ui.catalog) renderPhotos(); };
  $("split-range").oninput = event => $("viewer").style.setProperty("--split", event.target.value + "%");
  $("reset-button").onclick = reset; $("retry-button").onclick = () => ui.catalog ? scheduleRender(0) : start();
  $("zoom-out").onclick = () => setZoom(ui.zoom - .25); $("zoom-in").onclick = () => setZoom(ui.zoom + .25); $("zoom-fit").onclick = () => setZoom(1);
  $("looks-previous").onclick = () => $("looks-grid").scrollBy({ left: -270, behavior: "smooth" }); $("looks-next").onclick = () => $("looks-grid").scrollBy({ left: 270, behavior: "smooth" });
  $("fullscreen-button").onclick = async () => { try { if (document.fullscreenElement) await document.exitFullscreen(); else await document.querySelector(".editor-panel").requestFullscreen(); } catch (_) { document.body.classList.toggle("expanded-editor"); } };
  $("about-button").onclick = $("sources-button").onclick = $("footer-version").onclick = about;
  $("about-done").onclick = $("close-about").onclick = () => $("about-dialog").close();
  $("about-dialog").onclick = event => { if (event.target === $("about-dialog")) { const rect = event.target.getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.target.close(); } };
  $("metric-info").onclick = () => toast($("metric-info").title);
  $("export-button").onclick = () => { if (!ui.result || ui.busy || ui.dirty) return; const link = el("a"); link.href = ui.result.download_url; link.download = `flash-chroma-${ui.photo.id}-${ui.preset.id}.png`; document.body.append(link); link.click(); link.remove(); toast("已开始下载原尺寸PNG，保留完整处理像素。"); };
  $("copy-button").onclick = async () => { if (!ui.photo || !ui.preset) return; const config = JSON.stringify({ photo: ui.photo.id, preset: ui.preset.id, stages: native() ? undefined : ui.stages, native_profile: ui.preset.native_profile, profile: ui.profile, weights: ui.weights, threads: ui.threads, result_current: Boolean(ui.result && !ui.busy && !ui.dirty), actual_config: !ui.busy && !ui.dirty ? ui.result?.config : undefined }, null, 2); try { await navigator.clipboard.writeText(config); toast("四级组合与性能参数已复制。"); } catch (_) { const url = URL.createObjectURL(new Blob([config], { type: "application/json" })); const link = el("a"); link.href = url; link.download = "flash-chroma-look.json"; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); toast("浏览器未开放剪贴板，已导出配置JSON。"); } };
  let panStart;
  $("viewer").addEventListener("pointerdown", event => { if (ui.zoom <= 1 || (ui.mode === "compare" && !event.altKey) || event.target.closest("button") || (event.target.closest("input") && !(event.altKey && event.target.id === "split-range"))) return; event.preventDefault(); panStart = { x: event.clientX, y: event.clientY, pan: [...ui.pan] }; $("viewer").setPointerCapture(event.pointerId); $("viewer").classList.add("panning"); });
  $("viewer").addEventListener("pointermove", event => { if (!panStart) return; ui.pan = [Math.max(-600, Math.min(600, panStart.pan[0] + event.clientX - panStart.x)), Math.max(-500, Math.min(500, panStart.pan[1] + event.clientY - panStart.y))]; applyZoom(); });
  for (const name of ["pointerup", "pointercancel"]) $("viewer").addEventListener(name, () => { panStart = null; $("viewer").classList.remove("panning"); });
  document.addEventListener("keydown", event => { if (event.code === "Space" && !event.repeat && !event.target.closest("input,select,textarea,button") && !$("about-dialog").open) { event.preventDefault(); ui.holdingOriginal = true; applyMode(); } if (event.key === "Escape") document.body.classList.remove("expanded-editor"); });
  document.addEventListener("keyup", event => { if (event.code === "Space" && ui.holdingOriginal) { ui.holdingOriginal = false; applyMode(); } }); window.addEventListener("blur", () => { if (ui.holdingOriginal) { ui.holdingOriginal = false; applyMode(); } });

  async function start() {
    try {
      const catalog = await api("/api/studio/catalog"); if (!catalog.photos?.length || !catalog.presets?.length || !Array.isArray(catalog.luts)) throw new Error("素材目录不完整，请检查工作台素材清单。");
      ui.catalog = catalog; renderEngine(catalog.engine); renderPhotoFilters(); renderLooks();
      text("about-photos", catalog.photos.length); text("about-looks", catalog.presets.length); text("about-luts", catalog.luts.length);
      choosePreset(catalog.default_preset || catalog.presets[0].id); choosePhoto(catalog.default_photo || catalog.photos[0].id);
      if (catalog.engine?.available === false) toast(catalog.engine.error || "本地运行库未就绪，素材仍可浏览。", true);
    } catch (error) { setBusy(false); $("viewer-empty").hidden = false; text("viewer-error", error.message); text("connection-status", "连接失败"); text("loading-text", "连接失败"); toast(error.message, true); }
  }
  applyMode(); start();
})();
