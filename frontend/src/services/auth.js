import { setAuthToken } from "./api";

const TOKEN_KEY = "booklender_token";

export function saveToken(tokenObj) {
  const token = tokenObj?.access_token || tokenObj;
  if (!token) return;
  localStorage.setItem(TOKEN_KEY, token);
  setAuthToken(token);
}

export function loadToken() {
  const t = localStorage.getItem(TOKEN_KEY);
  if (t) setAuthToken(t);
  return t;
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  setAuthToken(null);
}