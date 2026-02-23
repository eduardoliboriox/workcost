(function () {
  "use strict";

  function clamp(n, min, max) {
    return Math.max(min, Math.min(max, n));
  }

  function getCanvasBaseWidth(canvas) {
    // scrollWidth geralmente reflete a largura "real" do conteúdo
    // (principalmente quando há tabela/larguras internas).
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

    const availableWidth = wrapper.clientWidth || window.innerWidth;
    const baseWidth = getCanvasBaseWidth(canvas);

    const MIN_SCALE = 0.62;

    const scale = clamp(availableWidth / baseWidth, MIN_SCALE, 1);

    canvas.style.setProperty("--doc-scale", String(scale));

    requestAnimationFrame(() => {
      const rect = canvas.getBoundingClientRect();
      wrapper.style.height = Math.ceil(rect.height) + "px";
    });
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
