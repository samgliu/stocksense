import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  tracesSampleRate: 0,
  integrations: (defaultIntegrations) => {
    return defaultIntegrations.filter((integration) => integration.name !== 'BrowserSession');
  },
  replaysSessionSampleRate: 0,
  replaysOnErrorSampleRate: 0,
  sampleRate: 0.1,
});
