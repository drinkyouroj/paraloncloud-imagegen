import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

// Global error handler for uncaught errors
window.addEventListener('error', (event) => {
  // Suppress browser extension errors
  if (event.message && event.message.includes('Cannot redefine property: ethereum')) {
    event.preventDefault();
    console.warn('Suppressed browser extension error:', event.message);
    return false;
  }
});

// Handle unhandled promise rejections
window.addEventListener('unhandledrejection', (event) => {
  if (event.reason && event.reason.message && event.reason.message.includes('ethereum')) {
    event.preventDefault();
    console.warn('Suppressed browser extension promise rejection');
    return false;
  }
});

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
