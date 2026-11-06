import { buildPrompt } from "./prompt.js";

const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
const paras = s => String(s ?? "").split(/\n+/).filter(x => x.trim()).map(p => `<p>${esc(p)}</p>`).join("");
const store = {
  get(k, d) { try { const v = localStorage.getItem(k); return v === null ? d : JSON.parse(v); } catch { return d; } },
  set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); } catch {} },
  del(k) { try { localStorage.removeItem(k); } catch {} }
};

/* ================= Transliteration ================= */
const VOW = {a:["अ",""],A:["आ","ा"],i:["इ","ि"],I:["ई","ी"],u:["उ","ु"],U:["ऊ","ू"],f:["ऋ","ृ"],F:["ॠ","ॄ"],x:["ऌ","ॢ"],X:["ॡ","ॣ"],e:["ए","े"],E:["ऐ","ै"],o:["ओ","ो"],O:["औ","ौ"]};
const CON = {k:"क",K:"ख",g:"ग",G:"घ",N:"ङ",c:"च",C:"छ",j:"ज",J:"झ",Y:"ञ",w:"ट",W:"ठ",q:"ड",Q:"ढ",R:"ण",t:"त",T:"थ",d:"द",D:"ध",n:"न",p:"प",P:"फ",b:"ब",B:"भ",m:"म",y:"य",r:"र",l:"ल",v:"व",S:"श",z:"ष",s:"स",h:"ह",L:"ळ"};
const OTH = {M:"ं",H:"ः","~":"ँ","'":"ऽ"};
const R_VOW = {}, R_MAT = {}, R_CON = {}, R_OTH = {};
for (const [k, [i, m]] of Object.entries(VOW)) { R_VOW[i] = k; if (m) R_MAT[m] = k; }
for (const [k, v] of Object.entries(CON)) R_CON[v] = k;
for (const [k, v] of Object.entries(OTH)) R_OTH[v] = k;

function slp2dev(s) {
  let o = "";
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (CON[c]) { o += CON[c]; const n = s[i + 1]; if (n && VOW[n]) { o += VOW[n][1]; i++; } else o += "्"; }
    else if (VOW[c]) o += VOW[c][0];
    else if (OTH[c]) o += OTH[c];
    else o += c;
  }
  return o;
}
function dev2slp(s) {
  s = s.replace(/़/g, "");
  let o = "";
  for (let i = 0; i < s.length; i++) {
    const c = s[i];
    if (R_CON[c]) { o += R_CON[c]; const n = s[i + 1]; if (n === "्") { i++; continue; } if (R_MAT[n]) { o += R_MAT[n]; i++; continue; } o += "a"; }
    else if (R_VOW[c]) o += R_VOW[c];
    else if (R_OTH[c]) o += R_OTH[c];
    else o += c;
  }
  return o;
}
const IAST = [["ṭh","W"],["ḍh","Q"],["kh","K"],["gh","G"],["ch","C"],["jh","J"],["th","T"],["dh","D"],["ph","P"],["bh","B"],["ai","E"],["au","O"],
  ["ā","A"],["ī","I"],["ū","U"],["ṝ","F"],["ṛ","f"],["ḹ","X"],["ḷ","x"],["ṅ","N"],["ñ","Y"],["ṭ","w"],["ḍ","q"],["ṇ","R"],["ś","S"],["ṣ","z"],["ṃ","M"],["ṁ","M"],["ḥ","H"]];
function iast2slp(s) { s = s.normalize("NFC").toLowerCase(); for (const [a, b] of IAST) s = s.split(a).join(b); return s; }
const LET = new Set([...Object.keys(VOW), ...Object.keys(CON), "M", "H"]);
function toSlp(q) {
  q = q.trim();
  if (/[ऀ-ॿ]/.test(q)) return dev2slp(q);
  if (/[āīūṛṝḷṅñṭḍṇśṣṃḥ]/i.test(q)) return iast2slp(q);
  return q; // assume SLP1 / plain
}
const letters = k => [...k].filter(c => LET.has(c)).join("");
const normKey = k => { k = letters(k); return k.length > 1 && /[HM]$/.test(k) ? k.slice(0, -1) : k; };

/* ================= Kosha lookup ================= */
let INDEX = null;
const shardCache = new Map();
async function loadIndex() {
  if (!INDEX) INDEX = fetch("data/index.json").then(r => r.json()).then(a => new Set(a));
  return INDEX;
}
const fname = p => p.replace(/[A-Z]/g, c => c.toLowerCase() + "2");
async function shardFor(key) {
  const idx = await loadIndex();
  for (let n = Math.min(key.length, 9); n > 0; n--) {
    const p = key.slice(0, n);
    if (idx.has(p)) {
      if (!shardCache.has(p)) shardCache.set(p, fetch(`data/k/${fname(p)}.json`).then(r => r.ok ? r.json() : {}).catch(() => ({})));
      return shardCache.get(p);
    }
  }
  return {};
}
function candidates(raw) {
  const q = letters(toSlp(raw));
  const base = normKey(q);
  const list = [{ key: base, all: true }];
  const nominal = (stem, forms) => list.push({ key: normKey(stem), forms: new Set(forms) });
  const alt = stem => list.push({ key: normKey(stem), all: true });
  const b2 = base.slice(0, -2), b1 = base.slice(0, -1);
  if (/an$/.test(base)) nominal(b2 + "A", [b2 + "A"]);
  if (/in$/.test(base)) nominal(b2 + "I", [b2 + "I"]);
  if (/as$/.test(base)) nominal(b2 + "a", [b2 + "aH"]);
  if (/is$/.test(base)) nominal(b2 + "i", [b2 + "iH"]);
  if (/us$/.test(base)) nominal(b2 + "u", [b2 + "uH"]);
  if (/f$/.test(base)) nominal(b1 + "A", [b1 + "A"]);
  if (/[^a]A$/.test(base)) alt(b1 + "an");
  if (/am$/.test(base)) alt(b1);
  if (/ena$/.test(base)) alt(base.slice(0, -3) + "a");
  return list.filter(c => c.key);
}
async function lookup(raw) {
  const out = { s: [], v: [], k: [], m: [], a: [] };
  const seen = new Set();
  for (const c of candidates(raw)) {
    const e = (await shardFor(c.key))[c.key];
    if (!e) continue;
    for (const d of Object.keys(out)) {
      for (const item of e[d] || []) {
        if (!c.all) {
          if (d !== "s" && d !== "v") continue;
          if (!c.forms.has(letters(item[0]))) continue;
        }
        const sig = d + JSON.stringify(item).slice(0, 120);
        if (seen.has(sig)) continue;
        seen.add(sig); out[d].push(item);
      }
    }
  }
  return out;
}
async function neighbours(raw, limit = 40) {
  const base = normKey(letters(toSlp(raw)));
  if (base.length < 2) return [];
  const shard = await shardFor(base);
  return Object.keys(shard).filter(k => k.startsWith(base) && k !== base).slice(0, limit);
}

const KNAME = { s: "शब्दकल्पद्रुम", v: "वाचस्पत्यम्", k: "अमरकोश", m: "Monier-Williams", a: "Apte" };
const ORDER = ["s", "k", "v", "m", "a"];
function amaraRef(r) { const p = String(r || "").split("।"); return p.length >= 3 ? `${p[0]}.${p[1]}.${p[2]}` : r; }
function entryHTML(d, item) {
  if (d === "k") {
    return `<div class="kt"><div><b>${esc(item.h)}</b> ${item.g ? `(${esc(item.g)})` : ""} — ${esc(item.m)} <span class="ak-m">· अमरकोश ${esc(amaraRef(item.r))}</span></div>
      ${item.syn ? `<div class="ak-m">पर्याय: <span class="dv">${esc(item.syn.split(",").join(", "))}</span></div>` : ""}
      ${item.v ? `<div class="ak-v">${esc(item.v)}</div>` : ""}</div>`;
  }
  if (d === "s" || d === "v") return `<div class="kt clamp"><span class="dv"><b>${esc(slp2dev(item[0]))}</b> ${esc(slp2dev(item[1]))}</span></div>`;
  return `<div class="kt clamp">${esc(item)}</div>`;
}
function koshaBlock(head, res, note = "") {
  const rows = [];
  for (const d of ORDER) {
    const items = res[d];
    if (!items.length) continue;
    const shown = d === "m" ? items.slice(0, 12) : items.slice(0, 4);
    if (d === "m") {
      rows.push(`<div class="ke"><b>${KNAME[d]}</b><div class="kt clamp"><ol>${shown.map(t => `<li>${esc(t)}</li>`).join("")}</ol></div><button type="button" class="more">पूरा पढ़ें</button></div>`);
    } else {
      for (const it of shown) {
        const long = d !== "k";
        rows.push(`<div class="ke"><b>${KNAME[d]}</b>${entryHTML(d, it)}${long ? `<button type="button" class="more">पूरा पढ़ें</button>` : ""}</div>`);
      }
    }
  }
  return `<div class="kb"><div class="kb-h"><span>${esc(head)}</span>${note ? `<small>${esc(note)}</small>` : ""}</div>
    ${rows.length ? rows.join("") : `<div class="knone">कोशों में यह रूप नहीं मिला। प्रातिपदिक रूप से “कोश खोज” में खोजें।</div>`}</div>`;
}
document.addEventListener("click", e => {
  const b = e.target.closest(".more");
  if (!b) return;
  const t = b.previousElementSibling;
  const open = t.classList.toggle("clamp");
  b.textContent = open ? "पूरा पढ़ें" : "कम करें";
});
function hideUnneededMore(root) {
  requestAnimationFrame(() => root.querySelectorAll(".more").forEach(b => {
    const t = b.previousElementSibling;
    if (t && t.scrollHeight <= t.clientHeight + 2) b.hidden = true;
  }));
}

/* ================= Sample ================= */
const SAMPLE = {
  shloka_devanagari: "समदोषः समाग्निश्च समधातुमलक्रियः।\nप्रसन्नात्मेन्द्रियमनाः स्वस्थ इत्यभिधीयते॥",
  iast: "samadoṣaḥ samāgniśca samadhātumalakriyaḥ |\nprasannātmendriyamanāḥ svastha ityabhidhīyate ||",
  source: { text: "सुश्रुत संहिता, सूत्रस्थान 15/41", note: "कुछ संस्करणों में 15/48 · Doṣadhātumalakṣayavṛddhivijñānīya adhyāya", confidence: "high" },
  corrections: "",
  padaccheda: "समदोषः समाग्निः च समधातुमलक्रियः । प्रसन्न-आत्म-इन्द्रिय-मनाः स्वस्थः इति अभिधीयते ॥",
  anvaya: "(यः) समदोषः समाग्निः समधातुमलक्रियः च प्रसन्नात्मेन्द्रियमनाः (भवति, सः) ‘स्वस्थः’ इति अभिधीयते ।",
  words: [
    { pada: "समदोषः", lookup: ["सम", "दोष"], vigraha: "समाः दोषाः यस्य सः", grammar: "बहुव्रीहि समास · पुं. प्रथमा एकवचन",
      hi: "जिसके वात, पित्त और कफ — तीनों दोष सम (न बढ़े, न घटे) अवस्था में हों।", en: "One whose three doṣas — vāta, pitta and kapha — are in equilibrium.",
      ayurveda: "‘दूषयन्तीति दोषाः’ — साम्यावस्था में यही शरीर को धारण करते हैं।" },
    { pada: "समाग्निः", lookup: ["अग्नि"], vigraha: "समः अग्निः यस्य सः", grammar: "बहुव्रीहि समास · पुं. प्रथमा एकवचन",
      hi: "जिसकी जठराग्नि सम हो — न विषम, न तीक्ष्ण, न मन्द।", en: "One whose digestive fire is balanced — not irregular, sharp or weak.",
      ayurveda: "अग्नि के चार भेद — सम, विषम, तीक्ष्ण, मन्द; केवल समाग्नि स्वास्थ्य का लक्षण है।" },
    { pada: "च", lookup: [], vigraha: "", grammar: "अव्यय", hi: "और", en: "and", ayurveda: "" },
    { pada: "समधातुमलक्रियः", lookup: ["धातु", "मल", "क्रिया"], vigraha: "समाः धातवः मलाः (तेषां) क्रियाः च यस्य सः", grammar: "बहुव्रीहि समास · पुं. प्रथमा एकवचन",
      hi: "जिसके सातों धातु, मल (पुरीष, मूत्र, स्वेद) और उनकी क्रियाएँ सम हों।", en: "One whose seven dhātus, malas and their functions are in normal measure.",
      ayurveda: "डल्हण ‘क्रिया’ को धातु और मल दोनों से जोड़ते हैं — मात्रा और कर्म दोनों की समता।" },
    { pada: "प्रसन्नात्मेन्द्रियमनाः", lookup: ["प्रसन्न", "आत्मन्", "इन्द्रिय", "मनस्"], vigraha: "प्रसन्नाः आत्मा इन्द्रियाणि मनः च यस्य सः", grammar: "बहुव्रीहि समास · पुं. प्रथमा एकवचन",
      hi: "जिसकी आत्मा, इन्द्रियाँ और मन प्रसन्न हों।", en: "One whose soul, senses and mind are clear and content.",
      ayurveda: "स्वास्थ्य की मानसिक-आध्यात्मिक परिधि — केवल शारीरिक साम्य पर्याप्त नहीं।" },
    { pada: "स्वस्थः", lookup: ["स्वस्थ"], vigraha: "स्वस्मिन् तिष्ठति इति", grammar: "उपपद तत्पुरुष · पुं. प्रथमा एकवचन",
      hi: "जो अपनी स्व-प्रकृति में स्थित है।", en: "One established in one’s own natural state — healthy.", ayurveda: "‘स्व’ = प्रकृति; प्रकृति से च्युति ही विकृति है।" },
    { pada: "इति", lookup: [], vigraha: "", grammar: "अव्यय", hi: "ऐसा", en: "thus", ayurveda: "" },
    { pada: "अभिधीयते", lookup: ["अभिधा", "धा"], vigraha: "अभि + √धा", grammar: "कर्मणि लट्, प्रथम पुरुष एकवचन", hi: "कहा जाता है।", en: "is called.", ayurveda: "" }
  ],
  bhavartha_hi: "जिस व्यक्ति के दोष, अग्नि, धातु, मल और उनकी क्रियाएँ सम हों तथा जिसकी आत्मा, इन्द्रियाँ और मन प्रसन्न हों — उसे ‘स्वस्थ’ कहा जाता है।",
  bhavartha_en: "A person whose doṣas, agni, dhātus, malas and their functions are balanced, and whose soul, senses and mind are content, is called ‘svastha’ (healthy).",
  vyakhya_hi: "आचार्य सुश्रुत की यह परिभाषा स्वास्थ्य को केवल रोग के अभाव के रूप में नहीं, बल्कि एक सकारात्मक साम्य-अवस्था के रूप में देखती है। पूर्वार्ध में शारीरिक घटक हैं, उत्तरार्ध में मानसिक-आध्यात्मिक।\nरोगनिदान की दृष्टि से यह एक कसौटी है: परीक्षा में इन्हीं घटकों में से किसकी विकृति हुई है, यहीं से विकृति-विज्ञान आरम्भ होता है।",
  vyakhya_en: "Suśruta defines health as a positive state of balance, not merely the absence of disease. The first half lists bodily components, the second half psychological and spiritual ones.\nFor Roga Nidāna the verse is a reference standard: examination asks which of these components has departed from its natural state.",
  ayurveda_hi: "यह श्लोक आयुर्वेद के प्रयोजन ‘स्वस्थस्य स्वास्थ्यरक्षणम्’ का आधार है।",
  ayurveda_en: "The verse underpins Āyurveda’s first aim, preserving the health of the healthy.",
  terms: [], commentaries: []
};

/* ================= Render ================= */
const bi = (hi, en) => `<div class="bi"><div class="hi-only"><h3>हिन्दी</h3>${paras(hi)}</div><div class="en-only"><h3>English</h3>${paras(en)}</div></div>`;
const confTxt = { high: "", medium: "<small>(सम्भावित)</small>", low: "<small>(अनिश्चित — कृपया जाँचें)</small>", unknown: "<small>(स्रोत ज्ञात नहीं)</small>" };

function render(r, isSample) {
  const words = (r.words || []).map((w, i) => `
    <div class="word">
      <div><div class="pada">${esc(w.pada)}</div>
        ${w.vigraha ? `<div class="vig">${esc(w.vigraha)}</div>` : ""}
        ${w.grammar ? `<div class="gram">${esc(w.grammar)}</div>` : ""}</div>
      <div class="body">
        <div class="bi"><div class="hi-only"><p>${esc(w.hi)}</p></div><div class="en-only"><p>${esc(w.en)}</p></div></div>
        ${w.ayurveda ? `<div class="ayu"><strong>आयुर्वेदीय अर्थ:</strong> ${esc(w.ayurveda)}</div>` : ""}
        <div class="kosha-slot" data-i="${i}"></div>
      </div>
    </div>`).join("");
  const src = r.source || {};
  $("#out").innerHTML = `
  <article class="result">
    ${isSample ? `<div><span class="badge">उदाहरण · Sample</span></div>` : ""}
    <div class="verse">
      <p class="dev">${esc(r.shloka_devanagari)}</p>
      ${r.iast ? `<p class="iast">${esc(r.iast)}</p>` : ""}
      ${src.text ? `<div class="ref">— ${esc(src.text)} ${confTxt[src.confidence] || ""}${src.note ? `<br><small>${esc(src.note)}</small>` : ""}</div>` : ""}
      ${r.corrections ? `<div class="corr">संशोधन: ${esc(r.corrections)}</div>` : ""}
    </div>
    <section class="block"><h2>पदच्छेद <span>padaccheda</span></h2><div class="sk">${esc(r.padaccheda)}</div></section>
    <section class="block"><h2>अन्वय <span>anvaya · prose order</span></h2><div class="sk">${esc(r.anvaya)}</div></section>
    <section class="block"><h2>शब्दार्थ <span>हर शब्द के साथ मूल कोश-पाठ</span></h2><div class="words">${words}</div></section>
    <section class="block"><h2>भावार्थ <span>meaning</span></h2>${bi(r.bhavartha_hi, r.bhavartha_en)}</section>
    <section class="block"><h2>व्याख्या <span>explanation</span></h2>${bi(r.vyakhya_hi, r.vyakhya_en)}</section>
    ${(r.ayurveda_hi || r.ayurveda_en) ? `<section class="block"><h2>आयुर्वेदीय सन्दर्भ <span>Ayurvedic significance</span></h2>${bi(r.ayurveda_hi, r.ayurveda_en)}</section>` : ""}
    ${(r.terms || []).length ? `<section class="block"><h2>पारिभाषिक शब्द <span>technical terms</span></h2><div class="terms">${r.terms.map(t => `<div class="term"><div class="t">${esc(t.term)}</div><p class="hi-only">${esc(t.hi)}</p><p class="en-only">${esc(t.en)}</p></div>`).join("")}</div></section>` : ""}
    ${(r.commentaries || []).filter(c => c.name).length ? `<section class="block"><h2>टीकाकार मत <span>commentators</span></h2><div class="comm">${r.commentaries.filter(c => c.name).map(c => `<div class="c"><b>${esc(c.name)}</b><p class="hi-only">${esc(c.hi)}</p><p class="en-only">${esc(c.en)}</p></div>`).join("")}</div></section>` : ""}
    <div class="tools"><button class="btn ghost" type="button" id="copy">पूरा अर्थ कॉपी करें · Copy</button></div>
    <p class="note">शब्दार्थ के नीचे दिए कोश-पाठ सीधे शब्दकल्पद्रुम, वाचस्पत्यम्, अमरकोश, Monier-Williams और Apte के डिजिटल संस्करणों से हैं। पदच्छेद, अन्वय, भावार्थ और व्याख्या AI द्वारा बनाए गए हैं — शोध में उद्धृत करने से पहले मूल ग्रन्थ और टीका से मिलान करें।</p>
  </article>`;
  $("#copy").onclick = () => copyText(r);
  fillKoshas(r);
}
async function fillKoshas(r) {
  const slots = document.querySelectorAll(".kosha-slot");
  for (const slot of slots) {
    const w = r.words[+slot.dataset.i];
    const heads = (Array.isArray(w.lookup) ? w.lookup : String(w.lookup || "").split(/[,\s]+/)).filter(Boolean);
    if (!heads.length) continue;
    slot.innerHTML = `<div class="knone">कोश खोले जा रहे हैं…</div>`;
    try {
      const blocks = [];
      for (const h of heads.slice(0, 5)) blocks.push(koshaBlock(h, await lookup(h)));
      slot.innerHTML = `<div style="display:flex;flex-direction:column;gap:8px">${blocks.join("")}</div>`;
      hideUnneededMore(slot);
    } catch { slot.innerHTML = `<div class="knone">कोश-डेटा लोड नहीं हो सका।</div>`; }
  }
}
function plain(r) {
  const L = [r.shloka_devanagari, r.iast, r.source?.text ? `— ${r.source.text}` : "", "", "पदच्छेद: " + r.padaccheda, "अन्वय: " + r.anvaya, "", "शब्दार्थ:"];
  (r.words || []).forEach(w => { L.push(`• ${w.pada}${w.vigraha ? ` (${w.vigraha})` : ""} — ${w.hi} | ${w.en}`); if (w.ayurveda) L.push("   आयुर्वेद: " + w.ayurveda); });
  L.push("", "भावार्थ: " + r.bhavartha_hi, "Meaning: " + r.bhavartha_en, "", "व्याख्या:", r.vyakhya_hi, "", "Explanation:", r.vyakhya_en);
  if (r.ayurveda_hi) L.push("", "आयुर्वेदीय सन्दर्भ: " + r.ayurveda_hi, "Ayurvedic significance: " + r.ayurveda_en);
  return L.join("\n");
}
async function copyText(r) {
  const b = $("#copy"), t = plain(r);
  try { await navigator.clipboard.writeText(t); b.textContent = "कॉपी हो गया · Copied"; }
  catch { const ta = document.createElement("textarea"); ta.value = t; document.body.append(ta); ta.select(); try { document.execCommand("copy"); b.textContent = "कॉपी हो गया · Copied"; } catch { b.textContent = "कॉपी नहीं हुआ"; } ta.remove(); }
  setTimeout(() => b.textContent = "पूरा अर्थ कॉपी करें · Copy", 2000);
}

/* ================= AI (Gemini) ================= */
const DEFAULT_MODEL = "gemini-flash-latest";
const getKey = () => store.get("sb-key", "");
const getModel = () => store.get("sb-model", "") || DEFAULT_MODEL;

function parseJSON(text) {
  const t = String(text || "").trim().replace(/^```(?:json)?\s*/i, "").replace(/```\s*$/, "");
  try { return JSON.parse(t); } catch {}
  const a = t.indexOf("{"), b = t.lastIndexOf("}");
  if (a >= 0 && b > a) return JSON.parse(t.slice(a, b + 1));
  throw new Error("bad json");
}
async function callGemini(prompt, key, model) {
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${encodeURIComponent(model)}:generateContent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": key },
    body: JSON.stringify({ contents: [{ role: "user", parts: [{ text: prompt }] }], generationConfig: { responseMimeType: "application/json", temperature: 0.2 } })
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) { const e = new Error(j.error?.message || `HTTP ${r.status}`); e.status = r.status; throw e; }
  const text = (j.candidates?.[0]?.content?.parts || []).map(p => p.text || "").join("");
  if (!text) { const e = new Error(j.promptFeedback?.blockReason || "empty"); e.status = 0; throw e; }
  return text;
}
// Free-tier Gemini is often "overloaded" (503) or hits a per-model limit (429).
// Retry once, then fall back to other free models, each with its own quota.
const FALLBACK_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash", "gemini-2.5-flash-lite"];
const sleep = ms => new Promise(r => setTimeout(r, ms));
async function callWithFallback(prompt, key, onTry) {
  const models = [...new Set([getModel(), ...FALLBACK_MODELS])];
  let last;
  for (const m of models) {
    for (let attempt = 0; attempt < 2; attempt++) {
      onTry?.(m, attempt);
      try { return await callGemini(prompt, key, m); }
      catch (e) {
        last = e;
        if (e.status === 503 || e.status === 500) { if (attempt === 0) { await sleep(4000); continue; } break; }
        if (e.status === 429 || e.status === 404) break;   // try next model
        throw e;                                            // bad key etc.: stop
      }
    }
  }
  throw last;
}
async function explain(shloka, ref, depth) {
  const key = getKey();
  if (key) {
    const text = await callWithFallback(buildPrompt(shloka, ref, depth), key, (m, a) =>
      status($("#status"), a ? `Gemini व्यस्त है — दोबारा कोशिश (${m})…` : `श्लोक का विश्लेषण हो रहा है… (${m}, 20–60 सेकंड)`));
    return parseJSON(text);
  }
  // No personal key: try the site's own server function (only exists on a Vercel deployment).
  let r;
  try { r = await fetch("api/explain", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ shloka, ref, depth }) }); }
  catch { throw Object.assign(new Error("nokey"), { status: -1 }); }
  const ct = r.headers.get("content-type") || "";
  if (!ct.includes("json")) throw Object.assign(new Error("nokey"), { status: -1 });
  const j = await r.json();
  if (!r.ok) throw Object.assign(new Error(j.error || "server"), { status: r.status === 501 ? -1 : r.status });
  return parseJSON(j.text);
}
function aiError(e) {
  const m = String(e?.message || "");
  if (e?.status === -1) return `AI व्याख्या के लिए मुफ़्त Gemini key चाहिए। <a href="#settings" data-goto="settings">सेटिंग</a> में key डालें (2 मिनट लगते हैं)। तब तक “कोश खोज” बिना key के चलती है।`;
  if (e?.status === 429 || /quota|rate/i.test(m)) return "आज की मुफ़्त सीमा पूरी हो गई या बहुत जल्दी-जल्दी अनुरोध हुए। थोड़ी देर बाद फिर कोशिश करें।";
  if (e?.status === 400 && /key/i.test(m) || e?.status === 403) return `Gemini key सही नहीं लग रही। <a href="#settings" data-goto="settings">सेटिंग</a> में key दोबारा जाँचें।`;
  if (e?.status === 404) return `Model नहीं मिला। <a href="#settings" data-goto="settings">सेटिंग</a> में model “${DEFAULT_MODEL}” रखें।`;
  if (e?.status === 503 || e?.status === 500) return "Gemini के सभी मुफ़्त models अभी व्यस्त हैं (कई बार कोशिश की गई)। 2–3 मिनट बाद फिर ‘अर्थ खोजें’ दबाएँ।<br><small>Google: " + esc(m.slice(0, 140)) + "</small>";
  if (/json/i.test(m)) return "उत्तर ठीक से नहीं बन पाया — एक बार फिर ‘अर्थ खोजें’ दबाएँ।";
  if (e instanceof TypeError) return "इंटरनेट कनेक्शन जाँचें — AI व्याख्या के लिए इंटरनेट चाहिए।";
  return "कुछ गड़बड़ हुई: " + esc(m.slice(0, 160));
}

/* ================= UI wiring ================= */
function status(el, html, err) { el.innerHTML = html; el.classList.toggle("err", !!err); }
function setLang(l) {
  document.body.dataset.lang = l;
  document.querySelectorAll(".pill button").forEach(b => b.setAttribute("aria-pressed", b.dataset.l === l));
  store.set("sb-lang", l);
}
document.querySelectorAll(".pill button").forEach(b => b.onclick = () => setLang(b.dataset.l));
setLang(store.get("sb-lang", "both"));

function showTab(t) {
  if (!["shloka", "kosha", "settings"].includes(t)) t = "shloka";
  document.querySelectorAll("nav.tabs button").forEach(b => b.setAttribute("aria-selected", b.dataset.tab === t));
  for (const id of ["shloka", "kosha", "settings"]) $("#tab-" + id).hidden = id !== t;
  if (location.hash.slice(1) !== t) history.replaceState(null, "", "#" + t);
}
document.querySelectorAll("nav.tabs button").forEach(b => b.onclick = () => showTab(b.dataset.tab));
document.addEventListener("click", e => { const a = e.target.closest("[data-goto]"); if (a) { e.preventDefault(); showTab(a.dataset.goto); window.scrollTo({ top: 0 }); } });
window.addEventListener("hashchange", () => showTab(location.hash.slice(1)));
showTab(location.hash.slice(1) || "shloka");

// history
const loadHist = () => store.get("sb-hist", []);
function drawHist() {
  const h = loadHist();
  $("#historyBox").hidden = !h.length;
  $("#history").innerHTML = h.map((x, i) => `<li><button type="button" data-i="${i}">${esc((x.r.shloka_devanagari || x.q).split("\n")[0])}<small>${esc(x.r.source?.text || "")}</small></button></li>`).join("");
  $("#history").querySelectorAll("button").forEach(b => b.onclick = () => { const x = h[+b.dataset.i]; $("#shloka").value = x.q; render(x.r, false); $("#out").scrollIntoView({ behavior: "smooth" }); });
}
drawHist();

document.querySelectorAll(".tries button").forEach(b => b.onclick = () => { $("#shloka").value = b.dataset.s; $("#ref").value = b.dataset.r || ""; $("#shloka").focus(); });

$("#desk").addEventListener("submit", async e => {
  e.preventDefault();
  const st = $("#status"), q = $("#shloka").value.trim();
  if (!q) { status(st, "पहले श्लोक लिखें या पेस्ट करें।", true); return; }
  if (q.length > 2000) { status(st, "एक बार में एक-दो श्लोक ही डालें (2000 अक्षर तक)।", true); return; }
  const go = $("#go"); go.disabled = true;
  status(st, "श्लोक का विश्लेषण हो रहा है… (20–60 सेकंड)");
  try {
    const r = await explain(q, $("#ref").value.trim(), $("#depth").value);
    if (!r || !Array.isArray(r.words)) throw new Error("bad json");
    render(r, false); status(st, "");
    const h = loadHist().filter(x => x.q !== q); h.unshift({ q, r, t: Date.now() }); store.set("sb-hist", h.slice(0, 25)); drawHist();
    $("#out").scrollIntoView({ behavior: "smooth" });
  } catch (err) { status(st, aiError(err), true); }
  finally { go.disabled = false; }
});

// kosha search
async function koshaSearch(q) {
  const out = $("#kout");
  out.innerHTML = `<div class="knone">खोज रहे हैं…</div>`;
  try {
    const res = await lookup(q);
    const slp = normKey(letters(toSlp(q)));
    const near = await neighbours(q);
    out.innerHTML = koshaBlock(/[ऀ-ॿ]/.test(q) ? q : slp2dev(slp), res, slp ? `SLP1: ${slp}` : "") +
      (near.length ? `<div class="desk" style="gap:8px"><span class="lbl">इससे शुरू होने वाले शब्द</span><div class="hwlist">${near.map(k => `<button type="button" class="chipbtn" data-k="${esc(k)}">${esc(slp2dev(k))}</button>`).join("")}</div></div>` : "");
    out.querySelectorAll("[data-k]").forEach(b => b.onclick = () => { const d = slp2dev(b.dataset.k); $("#kq").value = d; koshaSearch(d); });
    hideUnneededMore(out);
  } catch { out.innerHTML = `<div class="knone">कोश-डेटा लोड नहीं हो सका। इंटरनेट जाँचें।</div>`; }
}
$("#kdesk").addEventListener("submit", e => { e.preventDefault(); const q = $("#kq").value.trim(); if (q) koshaSearch(q); });

// settings
$("#gkey").value = getKey();
$("#gmodel").value = store.get("sb-model", "");
$("#sdesk").addEventListener("submit", e => {
  e.preventDefault();
  store.set("sb-key", $("#gkey").value.trim());
  store.set("sb-model", $("#gmodel").value.trim());
  status($("#sstatus"), "सहेज लिया गया। अब “श्लोक व्याख्या” में अर्थ खोजें।");
});
$("#gclear").onclick = () => { store.del("sb-key"); $("#gkey").value = ""; status($("#sstatus"), "Key इस ब्राउज़र से हटा दी गई।"); };
$("#gtest").onclick = async () => {
  const key = $("#gkey").value.trim(), st = $("#sstatus");
  if (!key) { status(st, "पहले key डालें।", true); return; }
  status(st, "जाँच रहे हैं…");
  try { await callGemini('Reply with only this JSON: {"ok":true}', key, $("#gmodel").value.trim() || DEFAULT_MODEL); status(st, "Key ठीक है ✓ — अब सहेजें दबाएँ।"); }
  catch (e) { status(st, aiError(e), true); }
};

render(SAMPLE, true);

if ("serviceWorker" in navigator && location.protocol.startsWith("http")) {
  navigator.serviceWorker.register("sw.js").catch(() => {});
}
