// This script unregisters any existing service workers to prevent errors
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(registrations => {
    for (const registration of registrations) {
      registration.unregister();
      console.log('Service worker unregistered:', registration);
    }
  });
}
