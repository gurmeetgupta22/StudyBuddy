/**
 * StudyBuddy — API Client
 * Centralized HTTP layer with auth headers and error handling.
 */

import { pageUrl } from './routes.js';

const API_BASE = '/';

export function getToken() {
  return localStorage.getItem('sb_token');
}

export function setToken(token) {
  localStorage.setItem('sb_token', token);
}

export function clearToken() {
  localStorage.removeItem('sb_token');
  localStorage.removeItem('sb_user');
}

export function getUser() {
  try { return JSON.parse(localStorage.getItem('sb_user') || 'null'); }
  catch { return null; }
}

export function setUser(user) {
  localStorage.setItem('sb_user', JSON.stringify(user));
}

async function request(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(`${API_BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    clearToken();
    window.location.href = pageUrl('index');
    return;
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Request failed.' }));
    throw new Error(err.detail || 'Unknown error');
  }

  // Handle blob responses (PDF)
  const contentType = res.headers.get('content-type') || '';
  if (contentType.includes('application/pdf')) return res.blob();
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  // Auth
  getGoogleLoginUrl: () => `${API_BASE}auth/google/login`,

  // User
  getMe:          () => request('user/me'),
  submitSurvey:   (data) => request('user/survey', { method: 'POST', body: JSON.stringify(data) }),
  updateProfile:  (data) => request('user/profile', { method: 'PUT', body: JSON.stringify(data) }),

  // Notes
  generateNote:   (topic) => request('notes/generate', { method: 'POST', body: JSON.stringify({ topic }) }),
  listNotes:      () => request('notes/'),
  getNote:        (id) => request(`notes/${id}`),
  toggleBookmark: (id) => request(`notes/${id}/bookmark`, { method: 'POST' }),
  deleteNote:     (id) => request(`notes/${id}`, { method: 'DELETE' }),

  // Tests
  generateTest:   (data) => request('test/generate', { method: 'POST', body: JSON.stringify(data) }),
  listTests:      () => request('test/'),
  getTest:        (id) => request(`test/${id}`),
  submitScore:    (data) => request('test/score', { method: 'POST', body: JSON.stringify(data) }),
  deleteTest:     (id) => request(`test/${id}`, { method: 'DELETE' }),

  // Analytics
  getAnalytics:   () => request('analytics/'),

  // Export (returns Blob)
  exportNotePdf:  (id) => request(`export/notes/${id}/pdf`),
  exportTestPdf:  (id, answers = false) => request(`export/test/${id}/pdf?answers=${answers}`),
};
