import { API } from "../App";
import axios from "axios";

let notificationInterval = null;

export function registerServiceWorker() {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/sw.js").catch(() => {});
  }
}

export function startBreakingNewsPolling(onBreaking) {
  if (notificationInterval) return;

  const check = async () => {
    try {
      const r = await axios.get(`${API}/notifications/breaking`);
      if (r.data.count > 0) {
        const article = r.data.breaking[0];
        // In-app toast
        if (onBreaking) onBreaking(article);
        // Browser notification
        if ("Notification" in window && Notification.permission === "granted") {
          new Notification("Mint Street - Breaking", {
            body: article.title,
            icon: "/tvr-logo.png",
            tag: "tvr-breaking"
          });
        }
      }
    } catch {}
  };

  // Check on first load after a short delay
  setTimeout(check, 10000);
  // Then every 30 minutes
  notificationInterval = setInterval(check, 1800000);
}

export function requestNotificationPermission() {
  if ("Notification" in window && Notification.permission === "default") {
    Notification.requestPermission();
  }
}
