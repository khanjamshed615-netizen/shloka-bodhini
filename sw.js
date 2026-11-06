// Offline cache: the app shell up front, kosha shards as they are opened.
const V = "sb-v2";
const SHELL = ["./", "index.html", "app.js", "prompt.js", "manifest.webmanifest", "data/index.json",
  "fonts/TiroDevanagariSanskrit-Regular.ttf", "fonts/Mukta-Regular.ttf", "fonts/Mukta-Bold.ttf",
  "icons/icon-192.png", "icons/icon-512.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const u = new URL(e.request.url);
  if (e.request.method !== "GET" || u.origin !== location.origin || u.pathname.includes("/api/")) return;
  const isData = u.pathname.includes("/data/k/");
  if (isData) {
    // shards never change between versions: cache first
    e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => {
      if (r.ok) { const cp = r.clone(); caches.open(V).then(c => c.put(e.request, cp)); }
      return r;
    })));
    return;
  }
  // app files: network first so updates arrive, cache when offline
  e.respondWith(fetch(e.request).then(r => {
    if (r.ok) { const cp = r.clone(); caches.open(V).then(c => c.put(e.request, cp)); }
    return r;
  }).catch(() => caches.match(e.request).then(hit => hit || caches.match("index.html"))));
});
