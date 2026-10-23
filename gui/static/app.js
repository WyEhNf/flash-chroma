"use strict";
(() => {
  const $ = id => document.getElementById(id);
  const ui = { samples: [], jobs: [], sample: null, run: null, report: null, target: "sdr", mode: "compare", frame: 0, split: 50, playing: false, busy: false, polling: false, frameVersion: 0, reportVersion: 0, selectedJob: null, focusJob: null, libraryKey: "", logKey: "", browserPath: "", browserParent: null };
  let pollTimer, playTimer, sliderTimer;
  const text = (id, value) => { $(id).textContent = value; };
  const make = (tag, cls = "", value) => { const n = document.createElement(tag); n.className = cls; if (value !== undefined) n.textContent = value; return n; };
  const brand = name => ({ arri: "ARRI", red: "RED", blackmagic: "Blackmagic" }[String(name).toLowerCase()] || name || "RAW");
  const finite = n => n !== null && n !== undefined && Number.isFinite(Number(n));
  const number = (n, digits = 3) => finite(n) ? Number(n).toFixed(digits) : "—";
  const terminal = j => /^(completed|complete|done|success|succeeded|failed|error|cancelled|canceled)$/i.test(j.status || "");
  const succeeded = j => /^(completed|complete|done|success|succeeded)$/i.test(j.status || "");
  const failed = j => /^(failed|error)$/i.test(j.status || "");
  const status = j => ({ queued: "等待中", running: "处理中", completed: "已完成", complete: "已完成", done: "已完成", success: "已完成", succeeded: "已完成", failed: "失败", error: "失败", cancelled: "已取消", canceled: "已取消" }[String(j.status).toLowerCase()] || j.status || "等待中");
  const action = value => ({ first: "首帧处理", all: "完整素材处理", export: "导出", run: "素材处理", render: "素材处理" }[value] || value || "处理");
  const dimensions = s => s?.width && s?.height ? `${Number(s.width).toLocaleString()} × ${Number(s.height).toLocaleString()}` : "尺寸待解码";
  const frames = () => ui.run ? Math.max(0, Number(ui.report?.frames ?? ui.sample?.frames ?? 0)) : 0;
  const frameUrl = (kind, run = ui.run, frame = ui.frame, target = ui.target) => `/api/frame?${new URLSearchParams({ run, kind, frame: String(frame), target })}`;

  async function api(path, body) {
    const controller = new AbortController(), timer = setTimeout(() => controller.abort(), 20000);
    try {
      const options = { cache: "no-store", credentials: "same-origin", signal: controller.signal };
      if (body !== undefined) Object.assign(options, { method: "POST", headers: { "Content-Type": "application/json", "X-App-Token": window.APP_TOKEN || "" }, body: JSON.stringify(body) });
      const response = await fetch(path, options), raw = await response.text();
      let result;
      try { result = raw ? JSON.parse(raw) : {}; } catch { throw new Error(`无法解析本地服务响应（HTTP ${response.status}）`); }
      if (!response.ok || result.error) { const detail = result.message || result.error || result.detail || `HTTP ${response.status}`; throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail)); }
      return result;
    } catch (e) { if (e.name === "AbortError") throw new Error("本地服务响应超时，请检查任务日志。"); throw e; }
    finally { clearTimeout(timer); }
  }
  function toast(message, error = false) { const n = make("div", `toast${error ? " error" : ""}`, message); $("toast-region").append(n); setTimeout(() => n.remove(), error ? 8500 : 4500); }

  function renderLibrary() {
    text("sample-count", ui.samples.length);
    const key = JSON.stringify(ui.samples.map(s => [s.id, s.name, s.brand, s.run, s.available, s.width, s.height, s.frames])) + ui.sample?.id;
    if (key === ui.libraryKey) return;
    ui.libraryKey = key;
    const list = $("sample-list"); list.replaceChildren();
    if (!ui.samples.length) list.append(make("div", "quiet-state", "素材库为空，导入 RAW 开始。"));
    for (const s of ui.samples) {
      const button = make("button", `sample-card${s.id === ui.sample?.id ? " active" : ""}`), thumb = make("div", "sample-thumbnail"), info = make("div", "sample-card-info");
      button.type = "button"; button.setAttribute("aria-pressed", String(s.id === ui.sample?.id)); button.setAttribute("aria-label", `${brand(s.brand)} ${s.name}`);
      const placeholder = make("span", "sample-brand-placeholder", brand(s.brand).toUpperCase()); thumb.append(placeholder);
      if (s.run) { const image = make("img"); image.alt = `${s.name} 的真实参考首帧`; image.loading = "lazy"; image.src = frameUrl("reference", s.run, 0, "sdr"); image.onload = () => placeholder.remove(); image.onerror = () => image.remove(); thumb.append(image); }
      thumb.append(make("span", "sample-card-brand", brand(s.brand).toUpperCase()));
      if (s.run) thumb.append(make("span", "sample-card-ready", "已有结果"));
      info.append(make("strong", "", s.name), make("p", "", `${s.width ? `${s.width} × ${s.height}` : "待解码"} · ${s.frames ? `${s.frames} 帧` : "帧数待确认"}`));
      button.append(thumb, info); button.onclick = () => selectSample(s.id); list.append(button);
    }
  }
  function renderResults() {
    const choices = [];
    if (ui.sample?.run) choices.push([ui.sample.run, ui.sample.run.startsWith("baseline:") ? "既有完整验证结果" : "素材最近结果"]);
    for (const j of [...ui.jobs].reverse()) if (j.sample === ui.sample?.id && j.run && succeeded(j) && !choices.some(c => c[0] === j.run)) choices.push([j.run, `${action(j.action)} · ${j.id}`]);
    if (ui.run && !choices.some(c => c[0] === ui.run)) choices.push([ui.run, "当前任务结果"]);
    const select = $("result-select"); select.replaceChildren(); choices.forEach(c => select.append(new Option(c[1], c[0])));
    if (!choices.length) select.append(new Option("暂无结果", "")); select.disabled = !choices.length; select.value = ui.run || "";
    $("export-button").disabled = !ui.run || ui.busy; $("open-folder").disabled = $("open-report").disabled = !ui.run;
  }
  function renderMetrics() {
    const m = ui.report?.metrics?.[ui.target] || (ui.run === ui.sample?.run ? ui.sample?.metrics?.[ui.target] : null);
    text("metric-mae", number(m?.mae)); text("metric-max", number(m?.max));
    const validation = $("validation-status"); validation.className = "validation-status";
    if (m?.scalar_equal === true) { validation.classList.add("valid"); validation.replaceChildren(make("span", "", "✓"), document.createTextNode("同模型原生 / 标量字节一致")); }
    else if (m?.scalar_equal === false) { validation.classList.add("invalid"); validation.replaceChildren(make("span", "", "!"), document.createTextNode("同模型字节核对不一致")); }
    else validation.replaceChildren(make("span", "", "○"), document.createTextNode(ui.run ? "正在读取精度报告" : "等待结果"));
    const r = ui.report?.runtime, info = r?.[ui.target]?.info || r?.info || r;
    const parts = ["CPU 本地工作流"];
    if (info?.revision) parts.push(`修订 ${info.revision}`); if (info?.threads_requested) parts.push(`${info.threads_requested} 线程`);
    if (info?.actual?.direct?.enabled === 0) parts.push("普通 LUT 路径"); text("runtime-info", parts.join(" · "));
  }
  function renderTransport() {
    const count = frames(); ui.frame = Math.max(0, Math.min(ui.frame, Math.max(0, count - 1)));
    const slider = $("frame-slider"); slider.max = String(Math.max(0, count - 1)); slider.value = String(ui.frame); slider.disabled = count < 2;
    slider.style.setProperty("--range-percent", `${count > 1 ? ui.frame / (count - 1) * 100 : 0}%`);
    $("previous-frame").disabled = count < 1 || ui.frame <= 0; $("next-frame").disabled = count < 1 || ui.frame >= count - 1;
    $("play-button").disabled = count < 2; $("play-button").title = count < 2 ? "单帧素材，无连续帧可播放" : ui.playing ? "暂停预览" : "播放预览（最高 10 fps）";
    $("play-button").setAttribute("aria-label", $("play-button").title); text("play-button", ui.playing ? "Ⅱ" : "▶"); text("frame-counter", count ? `${ui.frame + 1} / ${count}` : "— / —");
  }
  function renderSample() {
    const s = ui.sample;
    text("camera-brand", s ? `${brand(s.brand).toUpperCase()} / ${s.model || "RAW"}` : "RAW 工作流"); text("sample-title", s?.name || "选择一份素材");
    const fpsLabel = ui.report?.fps_scope || s?.fps_scope ? "导出时间基24fps；源帧率未知" : s?.fps ? `${s.fps} fps` : "";
    text("sample-subtitle", s ? `${dimensions(s)} · ${s.frames ? `${s.frames} 帧` : "帧数待解码"}${fpsLabel ? ` · ${fpsLabel}` : ""}` : "浏览真实工作流的参考与原生处理结果");
    text("input-space-label", s?.input_space ? `${s.input_space} → ACEScct` : "摄影机 Log → ACEScct"); text("frame-size", dimensions(ui.report || s));
    $("source-badge").hidden = !ui.run; text("source-badge", /首帧|first/i.test(ui.report?.scope || "") ? "首帧验证结果" : ui.report && Number(ui.report.frames) < Number(s?.frames) ? "首帧子集结果" : ui.run?.startsWith("baseline:") ? "既有验证结果" : "任务处理结果");
    $("result-select").title = ui.report?.scope || "选择真实处理结果";
    $("process-first").disabled = $("process-all").disabled = !s || s.available === false || ui.busy;
    text("process-note", ui.executionWarning || (s?.available === false ? "原始文件当前不可用。已有结果仍可查看，请检查素材路径。" : "处理会重新执行 CPU 解码、Log 与四级 LUT。首帧模式仅验证子集。"));
    renderResults(); renderMetrics(); renderTransport();
  }
  function renderTarget() {
    document.querySelectorAll("[data-target]").forEach(b => { const active = b.dataset.target === ui.target; b.classList.toggle("active", active); b.setAttribute("aria-pressed", String(active)); });
    text("output-stage-title", ui.target === "hdr" ? "HDR 显示变换" : "SDR 显示变换"); text("output-stage-detail", ui.target === "hdr" ? "ACES 2.0 · Rec.2020 PQ · 1000 nits" : "ACES 2.0 · Rec.709 · 100 nits");
    text("preview-description", ui.mode === "difference" ? "误差图对照裁剪 RGB16 导出并放大 ×8；右侧数值对照未裁剪 float32。" : ui.target === "hdr" ? "HDR 经固定 SDR 映射预览；精度统计仍使用原 PQ 代码值。" : ui.mode === "compare" ? "拖动画面中的分割线，对比同一帧。" : "参考保留高精度处理，原生使用四级 RGB8 LUT。"); renderMetrics();
  }

  function empty(title, detail) { const n = $("stage-empty"); n.querySelector("strong").textContent = title; n.querySelector("p").textContent = detail; n.hidden = false; $("image-labels").hidden = $("preview-label").hidden = $("split-handle").hidden = true; }
  const loadImage = url => new Promise((resolve, reject) => { const img = new Image(); img.onload = () => resolve(img); img.onerror = () => reject(new Error("真实帧加载失败，请查看报告或任务日志后重试。")); img.src = url; });
  async function showFrame() {
    const version = ++ui.frameVersion; renderTransport();
    if (!ui.run) { $("stage-loading").hidden = true; empty("这份素材尚无处理结果", "选择已有结果，或点击“处理首帧”生成真实预览。"); ["runtime", "reference", "difference"].forEach(k => $("image-" + k).hidden = true); return; }
    $("stage-loading").hidden = false; $("stage-empty").hidden = true; $("image-labels").hidden = $("preview-label").hidden = $("split-handle").hidden = true;
    const kinds = ui.mode === "compare" ? ["reference", "runtime"] : [ui.mode];
    try {
      const images = await Promise.all(kinds.map(k => loadImage(frameUrl(k)))); if (version !== ui.frameVersion) return;
      ["runtime", "reference", "difference"].forEach(k => $("image-" + k).hidden = !kinds.includes(k)); kinds.forEach((k, i) => { $("image-" + k).src = images[i].src; });
      $("viewer-stage").dataset.mode = ui.mode; $("stage-empty").hidden = true; $("image-labels").hidden = false; $("right-label").hidden = ui.mode !== "compare";
      text("left-label", { compare: "参考 · float32 → 16bit", reference: "参考 · float32 → 16bit", runtime: "原生 · RGB8", difference: "真实误差图" }[ui.mode]);
      $("preview-label").hidden = false; text("preview-label", ui.mode === "difference" ? (ui.target === "hdr" ? "PQ代码差 ×8" : "导出RGB差 ×8") : ui.target === "hdr" ? "HDR → SDR 预览" : "SDR · Rec.709"); $("split-handle").hidden = ui.mode !== "compare";
    } catch (e) { if (version === ui.frameVersion) { stop(); empty("无法读取这帧画面", e.message); ["runtime", "reference", "difference"].forEach(k => $("image-" + k).hidden = true); } }
    finally { if (version === ui.frameVersion) $("stage-loading").hidden = true; }
  }
  function stop() { ui.playing = false; clearTimeout(playTimer); renderTransport(); }
  async function playStep() { if (!ui.playing || frames() < 2) return; ui.frame = (ui.frame + 1) % frames(); await showFrame(); if (ui.playing) playTimer = setTimeout(playStep, 1000 / Math.min(10, Number(ui.report?.fps || ui.sample?.fps || 10))); }
  async function setRun(run) {
    stop(); ui.run = run || null; ui.report = null; ui.frame = 0; const version = ++ui.reportVersion; renderSample(); showFrame(); if (!run) return;
    try { const report = await api(`/api/report?${new URLSearchParams({ run })}`); if (version === ui.reportVersion) { ui.report = report; renderSample(); if (Number(report.frames) === 1) stop(); } }
    catch (e) { if (version === ui.reportVersion) toast(`报告读取失败：${e.message}`, true); }
  }
  function selectSample(id) { const s = ui.samples.find(s => s.id === id); if (!s) return; stop(); ui.sample = s; ui.libraryKey = ""; renderLibrary(); const js = ui.jobs.filter(j => j.sample === id); if (js.length) ui.selectedJob = js[js.length - 1].id; setRun(s.run); renderJobs(); }

  function renderJobs() {
    const select = $("job-select"), currentOptions = [...select.options].map(o => o.value).join("|"), ids = [...ui.jobs].reverse().map(j => j.id).join("|");
    if (ids !== currentOptions) { select.replaceChildren(); for (const j of [...ui.jobs].reverse()) select.append(new Option("", j.id)); if (!ui.jobs.length) select.append(new Option("暂无任务", "")); }
    for (const option of select.options) { const item = ui.jobs.find(j => j.id === option.value); if (item) option.textContent = `${status(item)} · ${ui.samples.find(s => s.id === item.sample)?.name || item.sample || "素材"} · ${action(item.action)}`; }
    if (!ui.selectedJob || !ui.jobs.some(j => j.id === ui.selectedJob)) ui.selectedJob = ui.jobs[ui.jobs.length - 1]?.id || null;
    select.value = ui.selectedJob || ""; const j = ui.jobs.find(j => j.id === ui.selectedJob);
    text("job-status-tag", j ? status(j) : "就绪"); text("job-stage", j ? [j.stage, j.message].filter(Boolean).join(" · ") || status(j) : "选择素材后即可处理");
    const percent = j && finite(j.progress) ? Math.max(0, Math.min(100, Number(j.progress))) : null;
    $("job-progress-bar").style.width = `${percent ?? 0}%`; text("job-progress-text", percent !== null ? `${number(percent, 0)}%` : j ? "等待进度" : "—"); $("cancel-button").hidden = !j || terminal(j);
    const logs = j?.logs || [], key = JSON.stringify([j?.id, j?.status, logs, j?.message]);
    if (key !== ui.logKey) { ui.logKey = key; const n = $("log-content"), atBottom = n.scrollHeight - n.clientHeight - n.scrollTop < 35; n.replaceChildren();
      if (logs.length) logs.forEach(line => n.append(make("p", /失败|错误|error|failed/i.test(line) ? "log-error" : "", String(line))));
      else n.append(make("p", "log-muted", j ? "任务已创建，等待处理日志…" : "本地素材库已就绪。可直接浏览已有结果，或重新处理真实 RAW。"));
      if (j && failed(j) && j.message && !logs.some(line => String(line).includes(j.message))) n.append(make("p", "log-error", j.message)); if (atBottom) n.scrollTop = n.scrollHeight;
    } text("log-count", j ? `${j.id} · ${logs.length} 条` : "本地会话");
  }
  async function refresh(manual = false) {
    if (ui.polling) return; ui.polling = true; clearTimeout(pollTimer);
    try {
      const state = await api("/api/state"); ui.executionWarning = state.execution_warning || ""; ui.samples = Array.isArray(state.samples) ? state.samples : []; ui.jobs = Array.isArray(state.jobs) ? [...state.jobs].sort((a, b) => Number(a.created || 0) - Number(b.created || 0)) : [];
      $("connection-dot").className = "status-dot connected"; text("connection-label", ui.jobs.some(j => !terminal(j)) ? "本地任务运行中" : "本地服务已连接");
      if (!ui.sample && ui.samples.length) selectSample(ui.samples[0].id); else if (ui.sample) ui.sample = ui.samples.find(s => s.id === ui.sample.id) || ui.sample;
      renderLibrary(); renderSample(); renderJobs();
      if (ui.focusJob) { const j = ui.jobs.find(j => j.id === ui.focusJob); if (j && terminal(j)) { ui.focusJob = null; if (succeeded(j) && j.run) { if (j.sample === ui.sample?.id) setRun(j.run); toast(j.message || "任务完成，可查看真实处理结果。"); } else if (failed(j)) toast(j.message || "任务失败，请查看完整日志。", true); } }
      if (manual) toast("素材与任务状态已刷新。");
    } catch (e) { $("connection-dot").className = "status-dot error"; text("connection-label", "本地服务连接失败"); if (manual || !ui.samples.length) toast(e.message, true); if (!ui.samples.length) text("sample-list", "无法连接本地服务，请确认工作台已启动。"); }
    finally { ui.polling = false; pollTimer = setTimeout(() => refresh(), ui.jobs.some(j => !terminal(j)) ? 1000 : 5000); }
  }
  async function runTask(scope) { if (!ui.sample || ui.busy) return; ui.busy = true; renderSample(); try { const r = await api("/api/run", { sample: ui.sample.id, scope }); if (r.job?.id) ui.selectedJob = ui.focusJob = r.job.id; toast(scope === "first" ? "首帧任务已创建；结果仅覆盖首帧子集。" : "完整素材任务已创建。"); await refresh(); } catch (e) { toast(e.message, true); } finally { ui.busy = false; renderSample(); } }
  async function exportRun() { if (!ui.run || ui.busy) return; ui.busy = true; renderResults(); try { const r = await api("/api/export", { run: ui.run }); if (r.job?.id) ui.selectedJob = ui.focusJob = r.job.id; toast(r.message || "导出任务已提交，进度与验证结果见日志。"); await refresh(); } catch (e) { toast(e.message, true); } finally { ui.busy = false; renderSample(); } }

  let browserVersion = 0;
  async function browse(path = "") {
    const version = ++browserVersion; $("file-browser").hidden = false; text("browser-items", "正在读取目录…");
    try { const result = await api(`/api/browse?${new URLSearchParams({ path })}`); if (version !== browserVersion) return; ui.browserPath = result.path || ""; ui.browserParent = result.parent; text("browser-path", result.path || "工程目录"); $("browser-up").disabled = !result.parent || result.parent === result.path;
      const n = $("browser-items"); n.replaceChildren();
      for (const d of result.dirs || []) { const b = make("button", "browser-item"); b.type = "button"; b.append(make("i", "", "▱"), make("span", "", d.name)); b.onclick = () => browse(d.path); n.append(b); }
      for (const f of result.files || []) { if (!/\.(ari|r3d|braw)$/i.test(f.name)) continue; const b = make("button", "browser-item"); b.type = "button"; b.append(make("i", "", "◈"), make("span", "", f.name)); b.onclick = () => { $("import-path").value = f.path; $("import-brand").value = /\.ari$/i.test(f.name) ? "arri" : /\.r3d$/i.test(f.name) ? "red" : "blackmagic"; n.querySelectorAll(".selected").forEach(el => el.classList.remove("selected")); b.classList.add("selected"); }; n.append(b); }
      if (!n.childNodes.length) n.append(make("div", "quiet-state", "此目录没有子目录或支持的 RAW 文件。"));
    } catch (e) { if (version === browserVersion) text("browser-items", e.message); }
  }
  function bind() {
    $("refresh-button").onclick = () => refresh(true);
    document.querySelectorAll(".mode-switch button").forEach(b => { b.onclick = () => { stop(); ui.mode = b.dataset.mode; document.querySelectorAll(".mode-switch button").forEach(x => { const active = x.dataset.mode === ui.mode; x.classList.toggle("active", active); x.setAttribute("aria-pressed", String(active)); }); renderTarget(); showFrame(); }; });
    document.querySelectorAll("[data-target]").forEach(b => { b.onclick = () => { stop(); ui.target = b.dataset.target; renderTarget(); showFrame(); }; });
    const split = value => { ui.split = Math.max(0, Math.min(100, value)); $("image-area").style.setProperty("--split", `${ui.split}%`); $("split-handle").setAttribute("aria-valuenow", String(Math.round(ui.split))); }, handle = $("split-handle");
    handle.onpointerdown = e => { e.preventDefault(); handle.setPointerCapture(e.pointerId); }; handle.onpointermove = e => { if (handle.hasPointerCapture(e.pointerId)) { const rect = $("image-area").getBoundingClientRect(); split((e.clientX - rect.left) / rect.width * 100); } }; handle.onpointerup = e => { if (handle.hasPointerCapture(e.pointerId)) handle.releasePointerCapture(e.pointerId); };
    handle.onkeydown = e => { if (["ArrowLeft", "ArrowRight", "Home", "End"].includes(e.key)) { e.preventDefault(); e.stopPropagation(); split(e.key === "Home" ? 0 : e.key === "End" ? 100 : ui.split + (e.key === "ArrowRight" ? 2 : -2)); } };
    const step = value => { stop(); ui.frame = Math.max(0, Math.min(frames() - 1, Number(value))); showFrame(); };
    $("previous-frame").onclick = () => step(ui.frame - 1); $("next-frame").onclick = () => step(ui.frame + 1);
    $("frame-slider").oninput = e => { const value = Number(e.target.value); stop(); ui.frame = value; renderTransport(); clearTimeout(sliderTimer); sliderTimer = setTimeout(showFrame, 90); };
    $("play-button").onclick = () => { if (ui.playing) stop(); else if (frames() > 1) { ui.playing = true; renderTransport(); playStep(); } };
    $("viewer-stage").onkeydown = e => { if (e.target !== handle && ["ArrowLeft", "ArrowRight"].includes(e.key)) { e.preventDefault(); step(ui.frame + (e.key === "ArrowRight" ? 1 : -1)); } };
    $("result-select").onchange = e => setRun(e.target.value); $("job-select").onchange = e => { ui.selectedJob = e.target.value; renderJobs(); };
    $("process-first").onclick = () => runTask("first"); $("process-all").onclick = () => runTask("all"); $("export-button").onclick = exportRun;
    $("cancel-button").onclick = async () => { if (ui.selectedJob) try { const r = await api("/api/cancel", { job: ui.selectedJob }); toast(r.message || "已请求取消任务。"); await refresh(); } catch (e) { toast(e.message, true); } };
    for (const [id, kind] of [["open-folder", "folder"], ["open-report", "report"]]) $(id).onclick = async () => { if (ui.run) try { const r = await api("/api/open", { run: ui.run, kind }); if (r.message) toast(r.message); } catch (e) { toast(e.message, true); } };
    $("import-button").onclick = () => { $("import-error").hidden = true; $("import-dialog").showModal(); }; $("close-import").onclick = () => $("import-dialog").close(); $("browse-button").onclick = () => browse(ui.browserPath); $("browser-up").onclick = () => { if (ui.browserParent) browse(ui.browserParent); };
    $("import-form").onsubmit = async e => { e.preventDefault(); const path = $("import-path").value.trim(); if (!/\.(ari|r3d|braw)$/i.test(path)) { text("import-error", "请选择 .ari、.R3D 或 .braw 文件。"); $("import-error").hidden = false; return; } $("import-submit").disabled = true; $("import-error").hidden = true;
      try { const r = await api("/api/import", { path, brand: $("import-brand").value }); $("import-dialog").close(); toast("真实 RAW 素材已添加到本地素材库。"); await refresh(); if (r.sample?.id) selectSample(r.sample.id); }
      catch (err) { text("import-error", err.message); $("import-error").hidden = false; } finally { $("import-submit").disabled = false; }
    };
    document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
  }
  bind(); renderSample(); renderTarget(); refresh();
})();
