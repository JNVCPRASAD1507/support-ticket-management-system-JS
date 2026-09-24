
/**
 * Auth helpers
 */

async function login(email, password) {
  const data = await api.post("/auth/login", { email, password });
  localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
  const user = await api.get("/auth/me");
  localStorage.setItem(USER_KEY, JSON.stringify(user));
  return user;
}

async function register(name, email, password) {
  return api.post("/auth/register", { name, email, password });
}

async function logout() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  try {
    if (refreshToken) {
      await api.post("/auth/logout", { refresh_token: refreshToken });
    }
  } catch (_) {
    /* ignore */
  }
  clearAuth();
  window.location.href = "index.html";
}

function getCurrentUser() {
  const raw = localStorage.getItem(USER_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function isLoggedIn() {
  return !!localStorage.getItem(ACCESS_TOKEN_KEY);
}

function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = "index.html";
    return false;
  }
  return true;
}

function isAdmin() {
  const user = getCurrentUser();
  return user && user.role === "admin";
}

