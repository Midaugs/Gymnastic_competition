const API_BASE = "http://127.0.0.1:8000";

(function(){
  const n = Number(sessionStorage.getItem("reloadCount") || 0) + 1;
  sessionStorage.setItem("reloadCount", String(n));
  console.log("[boot] page load count:", n, "time:", new Date().toISOString());
  addEventListener("beforeunload", () => console.log("[unload] about to unload"));
})();

function getToken() {
  return localStorage.getItem("token");
}

function setToken(t) {
  localStorage.setItem("token", t);
}

function clearToken() {
  localStorage.removeItem("token");
}

 async function api(path, { method = "GET", body, auth = true } = {}) {
   const headers = { "Content-Type": "application/json" };
   if (auth && getToken()) headers.Authorization = "Bearer " + getToken();

   const res = await fetch(`${API_BASE}${path}`, {
     method,
     headers,
     body: body ? JSON.stringify(body) : undefined,
   });

   if (res.status === 401) {
     // Don’t redirect—surface the error so the UI stays visible
     throw new Error("Unauthorized (401). Please log in again.");
   }

   if (!res.ok) {
     const msg = await res.text();
     throw new Error(msg || `HTTP ${res.status}`);
   }
   const ct = res.headers.get("content-type") || "";
   return ct.includes("application/json") ? res.json() : res.blob();
}


export { API_BASE, api, getToken, setToken, clearToken };
