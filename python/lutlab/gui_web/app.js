"use strict";
const $ = (id) => document.getElementById(id);
const state = {data: null, busy: false, result: null, view: "compare", history: [], uploaded: [], stage: 0, uploadStage: 0, toastTimer: null};
const methodNames = {sample: "直接采样", ls_tetra_int: "最小二乘 / 整数", ls_tetra_jitter: "分层采样 / 整数"};
const icon = (name) => `<svg aria-hidden="true"><use href="#${name}"/></svg>`;
function toast(message) { $("toast").textContent = message; $("toast").hidden = false; clearTimeout(state.toastTimer); state.toastTimer = setTimeout(() => { $("toast").hidden = true; }, 7000); }
async function api(path, options = {}) {
  const response = await fetch(path, {...options, headers: {"X-Lutlab-Token": document.querySelector('meta[name="lutlab-token"]').content, ...(options.headers || {})}});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || `请求失败 (${response.status})`);
  return data;
}
const post = (path, value) => api(path, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(value)});
function option(value, text) { const result = document.createElement("option"); result.value = value; result.textContent = text; return result; }
function setPreset(preset) {
  for (let i = 0; i < 4; i++) $("source-" + i).value = `demo:${preset}:${i}`;
  document.querySelectorAll("[data-preset]").forEach((button) => button.classList.toggle("selected", button.dataset.preset === preset));
  dirty();
}
function buildStages() {
  for (let i = 0; i < 4; i++) {
    const field = document.createElement("div"); field.className = "stage-field";
    const number = document.createElement("span"); number.className = "stage-number"; number.textContent = String(i + 1).padStart(2, "0");
    const select = document.createElement("select"); select.id = "source-" + i; select.setAttribute("aria-label", `第${i + 1}级LUT`);
    for (const preset of state.data.presets) select.add(option(preset.id, preset.name));
    select.value = `demo:warm:${i}`; select.addEventListener("change", () => { document.querySelectorAll("[data-preset]").forEach((b) => b.classList.remove("selected")); dirty(); });
    const upload = document.createElement("button"); upload.className = "stage-upload"; upload.innerHTML = icon("upload"); upload.title = `导入第 ${i + 1} 级 LUT`; upload.setAttribute("aria-label", upload.title);
    upload.addEventListener("click", () => { state.uploadStage = i; $("lut-file").click(); });
    field.append(number, select, upload); $("stage-fields").append(field);
  }
  renderPipeline();
}
function renderPipeline() {
  $("pipeline").replaceChildren();
  for (let i = 0; i < 4; i++) {
    if (i) { const arrow = document.createElement("span"); arrow.innerHTML = icon("arrow"); arrow.style.color = "#c8c3d6"; arrow.style.display = "contents"; $("pipeline").append(arrow); }
    const model = state.result?.stages[i];
    const button = document.createElement("button"); button.className = "stage-block" + (state.stage === i ? " active" : "");
    const label = document.createElement("small"); label.textContent = `STAGE 0${i + 1}`;
    const name = document.createElement("b"); name.textContent = model?.name || $("source-" + i)?.selectedOptions[0]?.textContent || "待配置"; name.title = name.textContent;
    const size = document.createElement("span"); size.className = "stage-size"; size.textContent = `${model?.m || $("grid-size").value}³ · Q16 四面体`;
    button.append(label, name, size); button.addEventListener("click", () => { state.stage = i; renderPipeline(); drawLattice(); });
    $("pipeline").append(button);
  }
}
function drawLattice() {
  const canvas = $("lattice"), ctx = canvas.getContext("2d"); ctx.clearRect(0, 0, canvas.width, canvas.height);
  const project = ([r, g, b]) => [300 + (r - b) * 127, 250 - g * 145 - (r + b) * 42];
  ctx.strokeStyle = "#e8e2f1"; ctx.lineWidth = 1.5;
  for (let a = 0; a < 3; a++) for (let b = 0; b < 2; b++) for (let c = 0; c < 2; c++) {
    const p = [], q = []; let n = 0;
    for (let k = 0; k < 3; k++) if (k === a) {p.push(0); q.push(1);} else {p.push(n++ === 0 ? b : c); q.push(p[k]);}
    const u = project(p), v = project(q); ctx.beginPath(); ctx.moveTo(...u); ctx.lineTo(...v); ctx.stroke();
  }
  const model = state.result?.stages[state.stage];
  if (model) {
    const points = [...model.points].sort((a, b) => (a.xyz[0] + a.xyz[2]) - (b.xyz[0] + b.xyz[2]));
    for (const point of points) { const p = project(point.xyz); ctx.beginPath(); ctx.arc(...p, 3.5, 0, Math.PI * 2); ctx.fillStyle = `rgb(${point.rgb.join(",")})`; ctx.fill(); ctx.strokeStyle = "#ffffff88"; ctx.lineWidth = .8; ctx.stroke(); }
  }
  ctx.font = '17px "Segoe UI", sans-serif'; ctx.fillStyle = "#b4a6c7";
  for (const [point, text] of [[[1.13, 0, 0], "R"], [[0, 1.12, 0], "G"], [[0, 0, 1.13], "B"]]) {const p = project(point); ctx.fillText(text, p[0] - 5, p[1] + 9);}
  $("lattice-label").textContent = `第 ${state.stage + 1} 级`;
  $("lattice-caption").textContent = model ? `${model.m}³ 节点 · 抽样显示 ${model.points.length} 点` : "运行后显示实际节点抽样";
}
function dirty() {
  if (!state.busy && state.result) $("run-status").textContent = "配置已修改 · 下方保留上次结果";
  if (!state.result) { renderPipeline(); drawLattice(); }
}
function setBusy(busy) {
  state.busy = busy;
  for (const element of document.querySelectorAll(".config-body input,.config-body select,.config-body button,#demo,#image-select,#upload-image,#gallery-open,#mobile-gallery")) element.disabled = busy;
  $("run-status").classList.toggle("busy", busy);
  if (busy) $("run-status").classList.remove("error");
  $("progress-track").hidden = !busy;
  $("run").querySelector("span").textContent = busy ? "正在处理…" : "运行四级映射";
}
function chooseImage(id) {
  $("image-select").value = id;
  if (!id) return;
  $("before").src = `/asset/${id}`; $("before").hidden = false; $("empty-preview").hidden = true;
  state.result = null; state.stage = 0;
  $("after").hidden = true; $("split").hidden = true; $("split-line").hidden = true; $("before-tag").hidden = false; $("after-tag").hidden = true;
  $("image-size").textContent = "正在读取图片";
  $("before").onload = () => { $("image-size").textContent = `${$("before").naturalWidth} × ${$("before").naturalHeight}`; };
  for (const key of ["mean", "rms", "p99", "max"]) $(key).textContent = "—";
  $("metric-detail").textContent = "完成映射后，在这里查看完整图片的误差分布。";
  $("export-image").disabled = true; $("export-bundle").disabled = true;
  $("node-size").textContent = "—"; $("compression").textContent = "等待运行";
  $("result-title").textContent = "开始一次新的色彩实验"; $("result-subtitle").textContent = "本地计算 · 四级独立映射 · 不改动原始素材";
  $("run-status").textContent = "准备就绪"; $("preview-notice").hidden = true; setView("compare"); renderPipeline(); drawLattice();
}
function setView(view) {
  state.view = view;
  document.querySelectorAll("[data-view]").forEach((button) => button.classList.toggle("selected", button.dataset.view === view));
  $("viewer").className = "viewer " + view;
  const result = state.result, compare = view === "compare" && result;
  $("split").hidden = !compare; $("split-line").hidden = !compare;
  $("before-tag").hidden = !compare && !!result;
  $("after-tag").hidden = !result;
  $("preview-notice").hidden = true;
  if (!result) return;
  if (view === "heatmap" && !result.metrics) {
    $("after").hidden = true; $("before").hidden = false; $("preview-notice").textContent = "缺少完整参考，无法计算误差热图"; $("preview-notice").hidden = false;
    $("after-tag").hidden = true; return;
  }
  $("before").hidden = false; $("after").hidden = false;
  $("after").src = view === "heatmap" ? result.urls["heatmap.png"] : result.urls["output.png"];
  $("after-tag").textContent = view === "heatmap" ? `误差热图 · 0–${Math.max(result.metrics.max, 1).toFixed(2)}` : "映射结果";
  $("preview-caption").textContent = view === "heatmap" ? "冷色低误差 → 暖色高误差 · 对比完整四级参考" : (view === "compare" ? "拖动分割线对比 · 左原图 / 右映射" : "四级 Q16 四面体映射 · 完整图片");
}
async function upload(file, kind) {
  if (file.size > 64 * 1024 * 1024) throw new Error("文件最大为 64 MiB");
  return api(`/api/upload?kind=${kind}&name=${encodeURIComponent(file.name)}`, {method: "POST", headers: {"Content-Type": "application/octet-stream"}, body: file});
}
async function run() {
  if (state.busy) return;
  if (!$("image-select").value) return toast("请先选择或上传图片");
  if (!$("threshold").checkValidity()) { $("threshold").reportValidity(); return; }
  const request = {image: $("image-select").value, sources: [0, 1, 2, 3].map((i) => $("source-" + i).value), m: Number($("grid-size").value), method: $("method").value, grid: $("grid").value, backend: $("backend").value, threshold: Number($("threshold").value)};
  setBusy(true); $("run-status").textContent = "正在提交任务"; $("progress-bar").style.width = "2%";
  try {
    const job = await post("/api/run", request);
    await trackJob(job.id);
  } catch (error) { $("run-status").textContent = error.message; $("run-status").className = "run-status error"; toast(error.message); }
  finally { setBusy(false); }
}
async function trackJob(id) {
  for (;;) {
    const current = await api(`/api/job/${id}`);
    $("run-status").textContent = current.message;
    $("progress-bar").style.width = current.progress + "%";
    if (current.status === "failed") throw new Error(current.message);
    if (current.status === "done") {
      if (!state.history.some((job) => job.id === id)) state.history.unshift({id, result: current.result});
      showResult(current.result); renderHistory(); return;
    }
    await new Promise((resolve) => setTimeout(resolve, 700));
  }
}
function restoreParameters(parameters) {
  $("image-select").value = parameters.image;
  for (let i = 0; i < 4; i++) $("source-" + i).value = parameters.sources[i];
  for (const [id, key] of [["grid-size", "m"], ["method", "method"], ["grid", "grid"], ["backend", "backend"], ["threshold", "threshold"]]) $(id).value = parameters[key];
  $("grid-label").textContent = `${parameters.m} × ${parameters.m} × ${parameters.m}`;
  document.querySelectorAll("[data-preset]").forEach((button) => button.classList.toggle("selected", parameters.sources.every((s, i) => s === `demo:${button.dataset.preset}:${i}`)));
}
function showResult(result) {
  state.result = result; state.stage = 0;
  $("before").src = result.urls["input.png"]; $("before").hidden = false; $("empty-preview").hidden = true;
  $("image-size").textContent = `${result.image.width} × ${result.image.height}`;
  $("metric-scope").textContent = "当前图片 · 对比完整四级参考";
  for (const key of ["mean", "rms", "p99", "max"]) $(key).textContent = result.metrics ? result.metrics[key].toFixed(4) : "—";
  const metrics = result.metrics;
  $("metric-detail").textContent = metrics ? `最坏 1% 均值 ${metrics.cvar_1pct.toFixed(4)}　·　ΔE ≥ ${metrics.threshold}：${(metrics.fraction_ge_threshold * 100).toFixed(2)}%　·　最坏像素 (${metrics.worst_xy.join(", ")})` : "未提供全部四张完整 LUT；可查看映射结果，误差指标与热图不可用。";
  $("node-size").textContent = `${(result.node_bytes / 1024).toFixed(1)} KiB`;
  $("compression").textContent = `节点压缩 ${(4 * 256 ** 3 * 3 / result.node_bytes).toFixed(0)}×`;
  $("result-title").textContent = `映射已完成 · ${result.image.name}`;
  $("result-subtitle").textContent = `${result.backend}　·　任务 ${result.task_seconds.toFixed(2)} s（含拟合等步骤，非基准）　·　${result.image.competition_size ? "1024×768" : "非题目尺寸预览"}`;
  $("run-status").textContent = "映射完成 · 结果已保存至本机会话目录";
  $("export-image").disabled = false; $("export-bundle").disabled = false;
  setView(state.view); renderPipeline(); drawLattice();
}
function download(name) {
  if (!state.result) return;
  const a = document.createElement("a"); a.href = state.result.urls[name]; a.download = name === "output.png" ? "flash-chroma-output.png" : "flash-chroma-results.zip"; a.click();
}
function renderHistory() {
  $("history-body").replaceChildren(); $("history-empty").hidden = state.history.length > 0;
  state.history.forEach((item, i) => {
    const r = item.result, row = document.createElement("tr");
    for (const text of [`#${String(state.history.length - i).padStart(2, "0")}`, r.image.name, `${r.stages.map((s) => s.m).join("/")} · ${methodNames[r.parameters.method]}`, r.metrics?.mean.toFixed(4) ?? "无参考", r.metrics?.max.toFixed(4) ?? "—"]) {const td = document.createElement("td"); td.textContent = text; row.append(td);}
    const td = document.createElement("td"), button = document.createElement("button"); button.className = "button secondary"; button.textContent = "查看结果";
    button.addEventListener("click", () => { if (state.busy) return toast("请等待当前任务完成"); restoreParameters(r.parameters); showResult(r); setPage("workspace"); }); td.append(button); row.append(td); $("history-body").append(row);
  });
}
function setPage(page) {
  $("workspace-page").hidden = page !== "workspace"; $("history-page").hidden = page !== "history";
  $("page-title").textContent = page === "history" ? "本次运行记录" : "色彩工作台";
  document.querySelectorAll("[data-page]").forEach((button) => button.classList.toggle("active", button.dataset.page === page));
}
function renderGallery() {
  const query = $("photo-search").value.trim().toLowerCase(); $("gallery-grid").replaceChildren();
  for (const photo of state.data.photos.filter((p) => `${p.name} ${p.group}`.toLowerCase().includes(query))) {
    const button = document.createElement("button"); button.className = "gallery-tile"; button.disabled = state.busy;
    const img = document.createElement("img"); img.loading = "lazy"; img.src = photo.url + "?thumbnail=1"; img.alt = photo.name;
    const label = document.createElement("span"); label.textContent = photo.name; const group = document.createElement("small"); group.textContent = photo.group; label.append(group);
    button.append(img, label); button.addEventListener("click", () => { if (state.busy) return; chooseImage(photo.id); $("gallery-dialog").close(); setPage("workspace"); }); $("gallery-grid").append(button);
  }
}
async function start() {
  try {
    state.data = await api("/api/bootstrap"); $("photo-count").textContent = state.data.photos.length;
    buildStages(); $("image-select").replaceChildren(option("", "选择图片素材"));
    for (const photo of state.data.photos) $("image-select").add(option(photo.id, `${photo.group.toUpperCase()} / ${photo.name}`));
    for (const asset of state.data.uploads) {
      if (asset.kind === "image") $("image-select").add(option(asset.id, `上传 / ${asset.name}`));
      else for (let i = 0; i < 4; i++) $("source-" + i).add(option(asset.id, `${asset.name}${asset.m ? ` · ${asset.m}³` : " · 完整表"}`));
    }
    if (state.data.native) $("backend").add(option("native", "原生 CPU · auto"));
    if (state.data.photos.length) chooseImage(state.data.photos[0].id);
    state.history = state.data.history;
    if (state.history.length) { restoreParameters(state.history[0].result.parameters); showResult(state.history[0].result); }
    drawLattice(); renderHistory();
    if (state.data.active) {
      restoreParameters(state.data.active.request); setBusy(true);
      try { await trackJob(state.data.active.id); }
      finally { setBusy(false); }
    }
  } catch (error) { toast(`初始化失败：${error.message}`); $("run").disabled = true; }
}
$("image-select").addEventListener("change", () => chooseImage($("image-select").value));
$("grid-size").addEventListener("input", () => { const m = $("grid-size").value; $("grid-label").textContent = `${m} × ${m} × ${m}`; dirty(); });
for (const id of ["method", "grid", "backend", "threshold"]) $(id).addEventListener("change", dirty);
document.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.view)));
document.querySelectorAll("[data-preset]").forEach((button) => button.addEventListener("click", () => setPreset(button.dataset.preset)));
document.querySelectorAll("[data-page]").forEach((button) => button.addEventListener("click", () => setPage(button.dataset.page)));
$("split").addEventListener("input", () => { $("viewer").style.setProperty("--split", `${$("split").value}%`); });
$("run").addEventListener("click", run);
$("demo").addEventListener("click", () => { if (!state.data) return; setPreset("warm"); $("grid-size").value = "17"; $("grid-size").dispatchEvent(new Event("input")); $("method").value = "sample"; $("grid").value = "uniform"; $("backend").value = "numpy"; if (!$("image-select").value && state.data.photos.length) chooseImage(state.data.photos[0].id); run(); });
$("export-image").addEventListener("click", () => download("output.png")); $("export-bundle").addEventListener("click", () => download("results.zip"));
$("upload-image").addEventListener("click", () => $("image-file").click());
$("image-file").addEventListener("change", async (event) => { const file = event.target.files[0]; if (!file || state.busy) return; setBusy(true); $("run-status").textContent = "正在上传图片"; try { const record = await upload(file, "image"); $("image-select").add(option(record.id, `上传 / ${record.name}`)); chooseImage(record.id); } catch (error) { toast(error.message); } finally { event.target.value = ""; setBusy(false); } });
$("lut-file").addEventListener("change", async (event) => { const file = event.target.files[0]; if (!file || state.busy) return; const stage = state.uploadStage; setBusy(true); $("run-status").textContent = "正在上传 LUT"; try { const record = await upload(file, "lut"); for (let i = 0; i < 4; i++) $("source-" + i).add(option(record.id, `${record.name}${record.m ? ` · ${record.m}³` : " · 完整表"}`)); $("source-" + stage).value = record.id; document.querySelectorAll("[data-preset]").forEach((button) => button.classList.remove("selected")); toast(`已导入：${record.name}`); } catch (error) { toast(error.message); } finally { event.target.value = ""; setBusy(false); $("run-status").textContent = "准备就绪 · 已有结果保留上次配置"; dirty(); } });
$("gallery-open").addEventListener("click", () => { if (!state.data) return; renderGallery(); $("gallery-dialog").showModal(); });
$("help-open").addEventListener("click", () => $("help-dialog").showModal());
$("mobile-gallery").addEventListener("click", () => $("gallery-open").click());
$("mobile-help").addEventListener("click", () => $("help-dialog").showModal());
document.querySelectorAll(".close-dialog").forEach((button) => button.addEventListener("click", () => button.closest("dialog").close()));
$("photo-search").addEventListener("input", renderGallery);
document.addEventListener("keydown", (event) => { if ((event.ctrlKey || event.metaKey) && event.key === "Enter" && !$("workspace-page").hidden) { event.preventDefault(); run(); } });
start();
