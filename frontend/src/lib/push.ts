import api from './api';

const VAPID_PUBLIC_KEY_URL = '/notifications/vapid_public_key';
const SUBSCRIBE_URL = '/notifications/subscribe';

// Helper function to convert Base64 string to Uint8Array
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export async function registerAndSubscribe() {
  // 1. Check for service worker and push manager support
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    console.warn('Push messaging is not supported');
    return;
  }

  try {
    // 2. Register the service worker
    const registration = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered with scope:', registration.scope);

    // Wait for the service worker to become active
    await navigator.serviceWorker.ready;
    console.log('Service Worker is active.');

    // 3. Check for existing subscription
    let subscription = await registration.pushManager.getSubscription();
    if (subscription) {
      console.log('User is already subscribed.');
      // Optionally, you could re-send the subscription to the backend here
      // to ensure it's up-to-date, but it's often not necessary.
      return;
    }
    
    // 4. Get VAPID public key from the backend
    const response = await api.get(VAPID_PUBLIC_KEY_URL);
    const vapidPublicKey = response.data.public_key;
    if (!vapidPublicKey) {
      throw new Error('Could not fetch VAPID public key from server.');
    }
    const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);

    // 5. Subscribe the user
    console.log('Subscribing user for push notifications...');
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: applicationServerKey
    });

    if (!subscription) {
      throw new Error('Failed to subscribe user.');
    }

    console.log('User subscribed successfully:', subscription);

    // 6. Send the subscription object to the backend
    await api.post(SUBSCRIBE_URL, subscription.toJSON());
    console.log('Subscription sent to server.');

  } catch (error) {
    console.error('Failed to subscribe to push notifications:', error);
    // Handle permission denied error
    if (Notification.permission === 'denied') {
      console.warn('Permission for notifications was denied');
      // Here you might want to update the UI to inform the user
      // how to enable notifications if they wish to.
    }
  }
}
