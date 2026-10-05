// POST helper: redirects to login if the server says 401
async function post(url, body) {
  const res = await fetch(url, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(body || {})});
  if (res.status === 401) { location.href = "/login"; return null; }
  return res.json();
}

// Star rating
const stars = document.querySelectorAll(".star");
stars.forEach(s => s.addEventListener("click", async () => {
  const score = +s.dataset.score;
  const data = await post("/rate/" + s.parentElement.dataset.id, {score});
  if (!data) return;
  stars.forEach(x => x.classList.toggle("on", +x.dataset.score <= score));
  document.getElementById("avg").textContent = data.avg + "/5 (" + data.count + " ratings)";
}));

// Watchlist toggle
const wl = document.getElementById("wl-btn");
if (wl) wl.addEventListener("click", async () => {
  const data = await post("/watchlist/" + wl.dataset.id);
  if (data) wl.textContent = data.in_list ? "✓ In watchlist" : "+ Add to watchlist";
});
