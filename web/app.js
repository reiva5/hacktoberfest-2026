// Startup ASEAN Gateway UI. Talks to the pipeline only through the HTTP API.
// Shows match reasons and warnings exactly as returned; never recomputes eligibility.

const API = (window.API_BASE || "http://localhost:8000").replace(/\/$/, "");
const DECK_TIMEOUT_MS = 10 * 60 * 1000;

const ASEAN = {
  BN: "Brunei", KH: "Cambodia", ID: "Indonesia", LA: "Laos", MY: "Malaysia",
  MM: "Myanmar", PH: "Philippines", SG: "Singapore", TH: "Thailand", VN: "Vietnam",
};
const STAGES = { "idea": "Idea", "pre-seed": "Pre-seed", "seed": "Seed", "series-a+": "Series A+" };
const TYPES = {
  accelerator: "Accelerator", grant: "Grant", competition: "Competition", gov_scheme: "Government scheme",
  credits: "Credits", investment: "Investment", other: "Other",
};

const $ = (sel) => document.querySelector(sel);

// Page text comes from crawled sites: always escape it.
function esc(s) {
  return String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}
function safeUrl(u) {
  try { const x = new URL(u); return x.protocol === "https:" || x.protocol === "http:" ? x.href : null; } catch { return null; }
}
function host(u) { try { return new URL(u).hostname.replace(/^www\./, ""); } catch { return ""; } }
function isSample(p) { return /example\.org/.test(p.canonical_url || "") || /^SAMPLE DATA/i.test(p.summary || ""); }

async function api(path, opts = {}) {
  const res = await fetch(API + path, opts);
  if (!res.ok) {
    let detail = res.statusText;
    try { detail = (await res.json()).detail || detail; } catch {}
    throw new Error(`${res.status}: ${detail}`);
  }
  return res.json();
}

function showApiError(err) {
  const el = $("#api-error");
  el.textContent = `Can't reach the API at ${API} (${err.message}). Start it with: python -m gateway serve`;
  el.hidden = false;
}

// ---------- Tabs ----------
document.querySelectorAll(".tab").forEach((t) => t.addEventListener("click", () => {
  document.querySelectorAll(".tab").forEach((x) => x.classList.toggle("active", x === t));
  document.querySelectorAll(".view").forEach((v) => (v.hidden = v.id !== `view-${t.dataset.view}`));
  if (t.dataset.view === "gap") loadGap();
}));

// ---------- Data banner ----------
// Say what kind of data is on screen. Sample records are fictional; crawled
// records haven't been checked by hand yet, so the totals aren't verified coverage.
function showDataBanner(all) {
  const el = $("#sample-banner");
  const samples = all.filter(isSample).length;
  const crawled = all.length - samples;
  if (!samples) { el.hidden = true; return; }
  const n = (k, word) => `${k} ${word}${k === 1 ? "" : "s"}`;
  el.innerHTML = crawled
    ? `Showing <b>mixed data</b>: ${n(samples, "fictional sample program")} (marked Sample) and ${n(crawled, "crawled program")} not yet checked by hand. The numbers above count both.`
    : "Showing <b>sample data</b>: these programs are fictional and only for building the UI.";
  el.hidden = false;
}

// ---------- Stats header ----------
async function loadStats() {
  try {
    const [s, all] = await Promise.all([api("/stats"), api("/programs?open_only=false")]);
    showDataBanner(all);
    const tiles = [
      [s.open_programs, "open programs"],
      [s.asean_countries_covered, "ASEAN countries covered"],
      [s.closing_in_30_days, "close in the next 30 days"],
      [s.not_on_aggregators, "not listed on any aggregator"],
    ];
    $("#stats").innerHTML = tiles.map(([n, l]) => `<div class="stat"><b>${esc(n)}</b><span>${esc(l)}</span></div>`).join("");
  } catch (e) { showApiError(e); }
}

// ---------- Profile form ----------
const countrySel = $("#f-country");
countrySel.innerHTML = Object.entries(ASEAN).map(([c, n]) => `<option value="${c}">${n}</option>`).join("");
$("#f-looking").innerHTML = Object.entries(TYPES).filter(([k]) => k !== "other")
  .map(([k, n]) => `<label class="chip"><input type="checkbox" value="${k}"> ${n}</label>`).join("");

const list = (s) => s.split(",").map((x) => x.trim()).filter(Boolean);

function fillProfile(p, evidence = {}) {
  $("#f-company").value = p.company || "";
  countrySel.value = ASEAN[p.country] ? p.country : "MY";
  $("#f-stage").value = p.stage || "pre-seed";
  $("#f-sectors").value = (p.sectors || []).join(", ");
  $("#f-nat").value = (p.founder_nationalities || []).join(", ");
  $("#f-equity").checked = !!p.wants_equity_free;
  document.querySelectorAll("#f-looking input").forEach((i) => (i.checked = (p.looking_for || []).includes(i.value)));
  document.querySelectorAll(".ev").forEach((el) => {
    const n = evidence[el.dataset.ev];
    el.textContent = n ? `slide ${n}` : "";
    el.hidden = !n;
  });
  $("#profile-hint").hidden = !Object.keys(evidence).length;
  $("#profile").hidden = false;
}

function readProfile() {
  return {
    company: $("#f-company").value.trim() || null,
    country: countrySel.value,
    stage: $("#f-stage").value,
    sectors: list($("#f-sectors").value).map((s) => s.toLowerCase()),
    founder_nationalities: list($("#f-nat").value).map((s) => s.toUpperCase()),
    wants_equity_free: $("#f-equity").checked,
    looking_for: [...document.querySelectorAll("#f-looking input:checked")].map((i) => i.value),
  };
}

$("#use-sample").addEventListener("click", () => fillProfile({ country: "MY", stage: "pre-seed" }));

$("#profile").addEventListener("submit", async (e) => {
  e.preventDefault();
  setMatchesLoading();
  try {
    const matches = await api("/match", {
      method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(readProfile()),
    });
    renderMatches(matches);
  } catch (err) { renderMatchError(err); }
});

// ---------- Deck upload ----------
let deckAbort = null;
let deckTimer = null;

const drop = $("#drop");
$("#deck-input").addEventListener("change", (e) => e.target.files[0] && uploadDeck(e.target.files[0]));
["dragenter", "dragover"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.add("over"); }));
["dragleave", "drop"].forEach((ev) => drop.addEventListener(ev, (e) => { e.preventDefault(); drop.classList.remove("over"); }));
drop.addEventListener("drop", (e) => { const f = e.dataTransfer.files[0]; if (f) uploadDeck(f); });
$("#cancel-deck").addEventListener("click", () => deckAbort && deckAbort.abort("cancelled"));

const PROGRESS_STEPS = [
  [0, "Reading your deck…"],
  [8, "Gemma is looking at each slide…"],
  [40, "Working out your country, stage and sectors…"],
  [120, "Still reading. Large decks take longer…"],
];

async function uploadDeck(file) {
  if (file.type && file.type !== "application/pdf") { showDeckError("Please upload a PDF."); return; }
  $("#deck-error").hidden = true;
  $("#deck-progress").hidden = false;
  drop.classList.add("busy");
  const started = Date.now();
  deckTimer = setInterval(() => {
    const s = Math.floor((Date.now() - started) / 1000);
    $("#progress-secs").textContent = s;
    $("#progress-text").textContent = PROGRESS_STEPS.filter(([t]) => s >= t).pop()[1];
  }, 500);
  deckAbort = new AbortController();
  const timeout = setTimeout(() => deckAbort.abort("timeout"), DECK_TIMEOUT_MS);
  setMatchesLoading("Waiting for your profile…");

  const body = new FormData();
  body.append("file", file);
  try {
    const res = await api("/deck", { method: "POST", body, signal: deckAbort.signal });
    fillProfile(res.profile, res.profile.evidence || {});
    renderMatches(res.matches);
  } catch (err) {
    const reason = deckAbort.signal.reason;
    if (reason === "timeout") showDeckError("Reading the deck took over 10 minutes, so we stopped. Fill in the form instead, or try a shorter deck.");
    else if (reason === "cancelled") showDeckError("Cancelled. You can fill in the form instead.");
    else showDeckError(`We couldn't read that deck (${err.message}). Fill in the form instead.`);
    fillProfile({ country: "MY", stage: "pre-seed" });
    resetMatches();
  } finally {
    clearTimeout(timeout);
    clearInterval(deckTimer);
    $("#deck-progress").hidden = true;
    drop.classList.remove("busy");
    $("#deck-input").value = "";
  }
}

function showDeckError(msg) { const el = $("#deck-error"); el.textContent = msg; el.hidden = false; }

// ---------- Match cards ----------
function setMatchesLoading(text = "Finding programs…") {
  $("#match-count").textContent = "";
  $("#matches").innerHTML = `<div class="empty">${esc(text)}</div>`;
}
function resetMatches() {
  $("#match-count").textContent = "";
  $("#matches").innerHTML = `<div class="empty">Upload a deck or fill in the form to see programs you qualify for, with the reasons.</div>`;
}
function renderMatchError(err) {
  $("#matches").innerHTML = `<div class="empty error">Couldn't load matches (${esc(err.message)}).</div>`;
}

function deadlineText(m) {
  const p = m.program;
  if (m.days_left != null) {
    if (m.days_left === 0) return { text: "Closes today", cls: "urgent" };
    return { text: `Closes in ${m.days_left} day${m.days_left === 1 ? "" : "s"}`, cls: m.days_left <= 14 ? "urgent" : m.days_left <= 30 ? "soon" : "" };
  }
  return { text: p.rolling ? "Rolling applications" : "No deadline stated", cls: "" };
}

function money(f) {
  if (!f || f.amount == null) return "";
  const n = new Intl.NumberFormat("en", { notation: f.amount >= 100000 ? "compact" : "standard", maximumFractionDigits: 1 }).format(f.amount);
  return `${f.currency ? esc(f.currency) + " " : ""}${n}`;
}

function verifiedOn(p) {
  if (!p.last_verified) return "not yet verified";
  return new Date(p.last_verified).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
}

function card(m) {
  const p = m.program;
  const dl = deadlineText(m);
  const url = safeUrl(p.canonical_url || p.program_url || p.source_url);
  const amount = money(p.funding);
  const equity = p.funding?.equity_free ? "Equity-free" : p.funding?.equity_pct ? `${p.funding.equity_pct}% equity` : "";
  const cs = p.countries || [];
  const where = !cs.length || cs.includes("*") ? "Open worldwide"
    : cs.length > 3 ? `${cs.length} ASEAN countries` : cs.map((c) => ASEAN[c] || c).join(", ");
  const summary = (p.summary || "").replace(/^SAMPLE DATA\.\s*/i, "");
  return `
  <article class="card">
    <div class="card-top">
      <div>
        <div class="meta">${esc(TYPES[p.type] || p.type)} · ${esc(where)}${isSample(p) ? ' <span class="tag sample">Sample</span>' : ""}</div>
        <h3>${esc(p.title)}</h3>
        <div class="org">${esc(p.organiser)}</div>
      </div>
      <div class="score" title="Match score"><b>${esc(m.score)}</b><span>match</span></div>
    </div>
    ${summary ? `<p class="summary">${esc(summary)}</p>` : ""}
    <div class="facts">
      <span class="deadline ${dl.cls}">${esc(dl.text)}</span>
      ${amount ? `<span>Up to ${amount}</span>` : ""}
      ${equity ? `<span>${esc(equity)}</span>` : ""}
    </div>
    <div class="why">
      <ul class="reasons">${(m.reasons || []).map((r) => `<li>${esc(r)}</li>`).join("")}</ul>
      ${(m.warnings || []).length ? `<ul class="warnings">${m.warnings.map((w) => `<li>${esc(w)}</li>`).join("")}</ul>` : ""}
    </div>
    <div class="source">
      ${url ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Organiser's page · ${esc(host(url))} ↗</a>` : "<span>No source link</span>"}
      <span>Verified ${esc(verifiedOn(p))}</span>
    </div>
  </article>`;
}

function renderMatches(matches) {
  $("#match-count").textContent = `${matches.length} program${matches.length === 1 ? "" : "s"}`;
  $("#matches").innerHTML = matches.length
    ? matches.map(card).join("")
    : `<div class="empty">No open programs match this profile in the sources crawled so far. Try a nearby stage, or untick some "Looking for" options.</div>`;
}

// ---------- Gap map ----------
async function loadGap() {
  try {
    const grid = await api("/gapmap");
    const stages = Object.keys(STAGES);
    const shade = (n) => (n === 0 ? "zero" : n <= 2 ? "low" : n <= 5 ? "mid" : "high");
    let empty = 0;
    const rows = Object.entries(grid).map(([c, row]) => {
      const cells = stages.map((s) => {
        const n = row[s] ?? 0;
        if (n === 0) empty++;
        return `<td class="${shade(n)}" title="${esc(ASEAN[c] || c)} · ${esc(STAGES[s])}: ${n} open">${n === 0 ? "—" : n}</td>`;
      }).join("");
      return `<tr><th scope="row">${esc(ASEAN[c] || c)}</th>${cells}</tr>`;
    }).join("");
    $("#gap").innerHTML = `<thead><tr><th></th>${stages.map((s) => `<th scope="col">${STAGES[s]}</th>`).join("")}</tr></thead><tbody>${rows}</tbody>`;
    const total = Object.keys(grid).length * stages.length;
    $("#gap-summary").innerHTML = `<b>${empty} of ${total}</b> country–stage combinations have no open program in our sources yet.`;
  } catch (e) { showApiError(e); }
}

// ---------- Add a program (paste a URL) ----------
const LANGS = {
  en: "English", id: "Bahasa Indonesia", ms: "Malay", vi: "Vietnamese", th: "Thai", km: "Khmer",
  lo: "Lao", my: "Burmese", tl: "Filipino", fil: "Filipino", zh: "Chinese",
};
const INGEST_STATUS = {
  ok: ["ok", "Done. Here's the structured record."],
  unchanged: ["ok", "This page hasn't changed since we last read it."],
  needs_review: ["warn", "Read, but the number of programs on this page changed a lot. A curator should check it."],
  not_program: ["warn", "That page doesn't look like a program or funding call."],
  error: ["error", "We couldn't read that page."],
};
const INGEST_STEPS = [
  [0, "Fetching the page…"],
  [5, "Cleaning the page text…"],
  [10, "Gemma is reading the page…"],
  [45, "Extracting eligibility, deadline and funding…"],
  [120, "Still working. Long pages take longer…"],
];
let ingestAbort = null;

function recordCard(p) {
  const url = safeUrl(p.canonical_url || p.program_url || p.source_url);
  const lang = p.language && p.language !== "en" ? (LANGS[p.language] || p.language) : "";
  const cs = p.countries || [];
  const where = !cs.length || cs.includes("*") ? "Open worldwide" : cs.map((c) => ASEAN[c] || c).join(", ");
  const deadline = p.deadline
    ? new Date(p.deadline).toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" })
    : p.rolling ? "Rolling" : "Not stated";
  const f = p.funding || {};
  const funding = [money(f), f.equity_free ? "equity-free" : f.equity_pct ? `${f.equity_pct}% equity` : ""].filter(Boolean).join(", ") || "Not stated";
  const row = (k, v) => `<div><dt>${k}</dt><dd>${v}</dd></div>`;
  return `
  <article class="card">
    <div class="meta">${esc(TYPES[p.type] || p.type)}${lang ? ` <span class="tag lang">Translated from ${esc(lang)}</span>` : ""}${isSample(p) ? ' <span class="tag sample">Sample</span>' : ""}</div>
    <h3>${esc(p.title)}</h3>
    <div class="org">${esc(p.organiser)}</div>
    ${p.summary ? `<p class="summary">${esc(p.summary.replace(/^SAMPLE DATA\.\s*/i, ""))}</p>` : ""}
    <dl class="record">
      ${row("Who can apply", esc(where))}
      ${row("Stages", esc((p.stages || []).map((s) => STAGES[s] || s).join(", ") || "Not stated"))}
      ${row("Sectors", esc((p.sectors || []).join(", ") || "Any"))}
      ${row("Funding", esc(funding))}
      ${row("Deadline", esc(deadline))}
    </dl>
    ${(p.eligibility || []).length ? `<div class="elig"><b>Eligibility</b><ul class="reasons">${p.eligibility.map((e) => `<li>${esc(e)}</li>`).join("")}</ul></div>` : ""}
    ${(p.issues || []).length ? `<ul class="warnings">${p.issues.map((i) => `<li>${esc(i)}</li>`).join("")}</ul>` : ""}
    <div class="source">
      ${url ? `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">Organiser's page · ${esc(host(url))} ↗</a>` : "<span>No source link</span>"}
      <span>Verified ${esc(verifiedOn(p))}</span>
    </div>
  </article>`;
}

function ingestNote(kind, text) {
  const el = $("#ingest-note");
  el.className = `note ${kind}`;
  el.textContent = text;
  el.hidden = false;
}

$("#cancel-ingest").addEventListener("click", () => ingestAbort && ingestAbort.abort("cancelled"));

$("#ingest-form").addEventListener("submit", async (e) => {
  e.preventDefault();
  const url = $("#ingest-url").value.trim();
  if (!safeUrl(url)) { ingestNote("error", "Please paste a full http(s) link."); return; }
  const btn = e.submitter || $("#ingest-form button");
  btn.disabled = true;
  $("#ingest-note").hidden = true;
  $("#ingest-results").innerHTML = "";
  $("#ingest-progress").hidden = false;
  const started = Date.now();
  const timer = setInterval(() => {
    const s = Math.floor((Date.now() - started) / 1000);
    $("#ingest-secs").textContent = s;
    $("#ingest-progress-text").textContent = INGEST_STEPS.filter(([t]) => s >= t).pop()[1];
  }, 500);
  ingestAbort = new AbortController();
  const timeout = setTimeout(() => ingestAbort.abort("timeout"), DECK_TIMEOUT_MS);
  try {
    const res = await api("/ingest", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }), signal: ingestAbort.signal,
    });
    const [kind, text] = INGEST_STATUS[res.status] || ["warn", `Status: ${res.status}`];
    const programs = (res.programs || []).filter(Boolean);
    const secs = Math.round((Date.now() - started) / 1000);
    ingestNote(kind, `${text}${programs.length ? ` ${programs.length} program${programs.length === 1 ? "" : "s"} in ${secs} s.` : ""}${res.note ? ` (${res.note})` : ""}`);
    $("#ingest-results").innerHTML = programs.map(recordCard).join("");
    if (programs.length) loadStats();
  } catch (err) {
    const reason = ingestAbort.signal.reason;
    if (reason === "timeout") ingestNote("error", "Reading the page took over 10 minutes, so we stopped.");
    else if (reason === "cancelled") ingestNote("warn", "Cancelled.");
    else ingestNote("error", `We couldn't read that page (${err.message}).`);
  } finally {
    clearTimeout(timeout);
    clearInterval(timer);
    $("#ingest-progress").hidden = true;
    btn.disabled = false;
  }
});

loadStats();
