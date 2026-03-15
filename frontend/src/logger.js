const LOG_ENDPOINT = import.meta.env.VITE_LOG_ENDPOINT || '/api/logs/frontend';

function sendLog(payload) {
  const body = JSON.stringify({
    ...payload,
    page: window.location.pathname,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString(),
  });

  if (navigator.sendBeacon) {
    const blob = new Blob([body], { type: 'application/json' });
    navigator.sendBeacon(LOG_ENDPOINT, blob);
    return;
  }

  fetch(LOG_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body,
    keepalive: true,
  }).catch(() => {
    // Ignore logger transport errors to avoid recursive logging.
  });
}

export function frontendLog(level, message, metadata = {}) {
  sendLog({ level, message, metadata });
}

export function setupFrontendErrorLogging() {
  window.addEventListener('error', (event) => {
    frontendLog('error', event.message || 'Unhandled error', {
      source: event.filename,
      line: event.lineno,
      column: event.colno,
      stack: event.error?.stack,
    });
  });

  window.addEventListener('unhandledrejection', (event) => {
    frontendLog('error', 'Unhandled promise rejection', {
      reason: event.reason?.message || String(event.reason),
      stack: event.reason?.stack,
    });
  });
}
