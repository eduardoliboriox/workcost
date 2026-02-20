(function () {
  "use strict";

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function getCanvasBaseWidth(canvas) {
    // Preferimos medir a largura "real" do conteúdo (sem depender de constante)
    // scrollWidth costuma refletir bem quando há conteúdo interno que define tamanho.
    // fallback para offsetWidth.
    return canvas.scrollWidth || canvas.offsetWidth || 1200;
  }

  function applyDocumentFit() {
    const wrapper = document.querySelector(".document-mobile-wrapper");
    const canvas = document.querySelector(".document-desktop-canvas");

    if (!wrapper || !canvas) return;

    const isMobile = window.matchMedia("(max-width: 768px)").matches;

    // Desktop: mantém comportamento existente
    if (!isMobile) {
      canvas.style.removeProperty("--doc-scale");
      wrapper.style.removeProperty("height");
      return;
    }

    // Largura disponível no wrapper (respeita padding do container)
    const availableWidth = wrapper.clientWidth || window.innerWidth;

    // Base width real do canvas (sem hardcode)
    const baseWidth = getCanvasBaseWidth(canvas);

    const scale = clamp(availableWidth / baseWidth, 0.1, 1);

    canvas.style.setProperty("--doc-scale", String(scale));

    // Ajusta altura do wrapper porque transform não afeta layout
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
