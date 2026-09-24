/**
 * Core API helper – all requests go through here.
 * Automatically attaches Bearer token and handles 401 refresh.
 */

async function apiRequest(method, path, body = null, isFormData = false) {
  const url = `${API_BASE_URL}${path}`;
  const headers = {};

  const accessToken = localStorage.getItem(ACCESS_TOKEN_KEY);
  if (accessToken) {
    headers["Authorization"] = `Bearer ${accessToken}`;
  }

  if (body && !isFormData) {
    headers["Content-Type"] = "application/json";
  }

  const options = {
    method,
    headers,
  };

  if (body) {
    options.body = isFormData ? body : JSON.stringify(body);
  }

  let response = await fetch(url, options);

  // Try refresh once on 401
  if (
    response.status === 401 &&
    path !== "/auth/login" &&
    path !== "/auth/refresh"
  ) {
    const refreshed = await tryRefreshToken();
    if (refreshed) {
      headers["Authorization"] =
        `Bearer ${localStorage.getItem(ACCESS_TOKEN_KEY)}`;
      response = await fetch(url, { ...options, headers });
    } else {
      clearAuth();
      window.location.href = "index.html";
      throw new Error("Session expired. Please login again.");
    }
  }

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    let message = `Request failed (${response.status})`;

    if (Array.isArray(data.detail)) {
      message = data.detail
        .map((d) => d.msg || d.message || JSON.stringify(d))
        .join(", ");
    } else if (typeof data.detail === "string") {
      message = data.detail;
    } else if (data.error?.message) {
      message = data.error.message;
    } else if (Array.isArray(data.error?.details)) {
      message = data.error.details
        .map((d) => `${d.field || "field"}: ${d.message || "Invalid value"}`)
        .join(", ");
    } else if (data.message) {
      message = data.message;
    }

    throw new Error(message);
  }

  return data;
}

async function tryRefreshToken() {
  const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) return false;

  try {
    const res = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (!res.ok) return false;
    const data = await res.json();
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access_token);
    localStorage.setItem(REFRESH_TOKEN_KEY, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

function clearAuth() {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// Convenience methods
const api = {
  get: (path) => apiRequest("GET", path),
  post: (path, body) => apiRequest("POST", path, body),
  put: (path, body) => apiRequest("PUT", path, body),
  patch: (path, body) => apiRequest("PATCH", path, body),
  delete: (path) => apiRequest("DELETE", path),
  upload: (path, formData) => apiRequest("POST", path, formData, true),
};
