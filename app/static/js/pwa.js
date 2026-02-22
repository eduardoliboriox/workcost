// PWA bootstrap (safe + minimal)
(function () {
  if (!("serviceWorker" in navigator)) return;

  window.addEventListener("load", function () {
    navigator.serviceWorker
      .register("/sw.js", { scope: "/" })
      .catch(function () {
        // silent fail (não quebra nada do app)
      });
  });
})();
