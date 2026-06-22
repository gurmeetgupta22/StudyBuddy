const ROUTE_MAP = {
  dashboard: 'a8xQ3m',
  notes: 'k7pR2n',
  test: 'x9mB4v',
  survey: 'j3nK8w',
  history: 't5Lp1d',
  analytics: 'c6rS9z',
  'auth-callback': 'f2gH7q',
};

export function pageUrl(name) {
  const slug = ROUTE_MAP[name];
  if (!slug) throw new Error('Unknown route: ' + name);
  if (name === 'index') return '/frontend/index.html';
  return '/frontend/pages/' + slug + '.html';
}

export function routeNameFromPath(path) {
  const m = path.match(/\/pages\/(.+)\.html/);
  if (!m) return null;
  const slug = m[1];
  for (const [name, s] of Object.entries(ROUTE_MAP)) {
    if (s === slug) return name;
  }
  return null;
}

export function redirectTo(name) {
  window.location.href = pageUrl(name);
}

window.__pageUrl = pageUrl;
window.__redirectTo = redirectTo;
