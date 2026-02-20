(function () {
  "use strict";

  const BASE_WIDTH = 1200;

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function applyDocumentFit() {
    const wrapper = document.querySelector(".document-mobile-wrapper");
    const canvas = document.querySelector(".document-desktop-canvas");

    if (!wrapper || !canvas) return;

    const isMobile = window.matchMedia("(max-width: 768px)").matches;

    // No desktop: não força fit (mantém layout normal)
    if (!isMobile) {
      canvas.style.removeProperty("--doc-scale");
      wrapper.style.removeProperty("height");
      return;
    }

    // Largura real disponível (já respeita padding do container)
    const availableWidth = wrapper.clientWidth || window.innerWidth;

    // escala proporcional ao BASE_WIDTH (1200px)
    const scale = clamp(availableWidth / BASE_WIDTH, 0.1, 1);

    canvas.style.setProperty("--doc-scale", String(scale));

    // Ajuste de altura para evitar corte, já que transform não impacta layout
    // Usa scrollHeight para pegar altura real do conteúdo
    const contentHeight = canvas.scrollHeight;
    wrapper.style.height = Math.ceil(contentHeight * scale) + "px";
  }

  let resizeTimer = null;

  function onResize() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(applyDocumentFit, 50);
  }

  document.addEventListener("DOMContentLoaded", applyDocumentFit);
  window.addEventListener("resize", onResize);
  window.addEventListener("orientationchange", applyDocumentFit);
})();
