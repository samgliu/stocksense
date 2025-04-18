import './index.css';
import './utils/sentry';
import App from './App';
import { Provider } from 'react-redux';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { store } from '@/app/store';
import * as Sentry from '@sentry/react';
import { ErrorElement } from './features/shared/ErrorElement';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <Sentry.ErrorBoundary fallback={<ErrorElement />}>
    <Provider store={store}>
      <App />
    </Provider>
  </Sentry.ErrorBoundary>,
);
