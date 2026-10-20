import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App.tsx";
import { registerServiceWorker } from "./utils/serviceWorker";
import { offlineService } from "./services/offline/OfflineService";

// Register service worker
registerServiceWorker().then((registration) => {
  if (registration) {
    console.log('[App] Service worker registered successfully');
  }
}).catch((error) => {
  console.error('[App] Service worker registration failed:', error);
});

// Initialize offline service
offlineService.init().then(() => {
  console.log('[App] Offline service initialized');
}).catch((error) => {
  console.error('[App] Offline service initialization failed:', error);
});

ReactDOM.createRoot(document.getElementById("root")!).render(<App />);
