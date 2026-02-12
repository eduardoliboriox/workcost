document.addEventListener("DOMContentLoaded", () => {

  if (localStorage.getItem("cookieConsent") === "accepted") {
    return;
  }

  const banner = document.createElement("div");
  banner.className = "cookie-banner";

  banner.innerHTML = `
    <div class="cookie-content">
      Utilizamos cookies para melhorar sua experiência.
      <a href="/cookie-policy" target="_blank">Saiba mais</a>
    </div>
    <div class="cookie-actions">
      <button id="acceptCookies" class="btn btn-sm btn-primary">
        Aceitar todos
      </button>
    </div>
  `;

  document.body.appendChild(banner);

  document.getElementById("acceptCookies")
    .addEventListener("click", () => {
      localStorage.setItem("cookieConsent", "accepted");
      banner.remove();
    });

});
