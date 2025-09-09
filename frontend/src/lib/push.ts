// frontend/src/lib/push.ts
import api from './api';

// This function converts the VAPID public key to a Uint8Array
function urlBase64ToUint8Array(base64String: string) {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export async function registerAndSubscribe(): Promise<void> {
  // 1. Check if service worker and push are supported
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn("Push messaging is not supported by this browser.");
    return;
  }

  const VAPID_PUBLIC_KEY = "BOsqN_7JTRbgQzc34nd9hqZ4hbI_jNWdvdGYo_ZpND1wvO7r9ZnRJxxVy1ooX50yrUHU4dlT_tuHi4j_r9pR2-M";
  if (!VAPID_PUBLIC_KEY) {
    console.error("VAPID_PUBLIC_KEY is not set in the frontend environment.");
    return;
  }

  try {
    // 2. Register the Service Worker
    const swRegistration = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered:', swRegistration);

    // 3. Request permission for notifications
    const permission = await window.Notification.requestPermission();
    if (permission !== 'granted') {
      console.warn('Notification permission not granted.');
      return;
    }

    // 4. Check for existing subscription
    let subscription = await swRegistration.pushManager.getSubscription();
    if (subscription === null) {
      // 5. If no subscription, create a new one
      console.log('No subscription found, creating new one.');
      subscription = await swRegistration.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
      });
      console.log('New subscription created:', subscription);

      // 6. Send the new subscription to the backend
      // The `api` client will automatically include the auth token.
      await api.post('/notifications/subscribe', subscription);
      console.log('Subscription sent to server.');
    } else {
      console.log('User is already subscribed:', subscription);
      // Optional: You could send the existing subscription to the server again
      // to ensure it's up-to-date, but it's often not necessary.
    }
  } catch (error) {
    console.error('Failed to register or subscribe for push notifications: ', error);
  }
}