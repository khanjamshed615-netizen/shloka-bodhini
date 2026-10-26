// Optional: only used when the site is deployed on Vercel with GEMINI_API_KEY set.
// Then visitors need no key of their own; all requests use the owner's free Gemini quota.
import { buildPrompt } from "../prompt.js";

export default async function handler(req, res) {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const key = process.env.GEMINI_API_KEY;
  if (!key) return res.status(501).json({ error: "no server key" });
  const { shloka = "", ref = "", depth = "detailed" } = req.body || {};
  if (!shloka.trim() || shloka.length > 2000 || ref.length > 200) return res.status(400).json({ error: "bad input" });
  const model = process.env.GEMINI_MODEL || "gemini-flash-latest";
  const r = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "x-goog-api-key": key },
    body: JSON.stringify({
      contents: [{ role: "user", parts: [{ text: buildPrompt(shloka, ref, depth === "brief" ? "brief" : "detailed") }] }],
      generationConfig: { responseMimeType: "application/json", temperature: 0.2 }
    })
  });
  const j = await r.json().catch(() => ({}));
  if (!r.ok) return res.status(r.status).json({ error: j.error?.message || "gemini error" });
  const text = (j.candidates?.[0]?.content?.parts || []).map(p => p.text || "").join("");
  return res.status(200).json({ text });
}
