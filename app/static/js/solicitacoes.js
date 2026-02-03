/**
 * solicitacoes.js
 * Script base da página de solicitações
 * Contém apenas funcionalidades comuns (neutras)
 */

document.addEventListener("DOMContentLoaded", () => {

  /* ===============================
     MULTISELECT - SETORES
     =============================== */

  const multiselect = document.getElementById("setoresSelect");
  const display = document.getElementById("setoresDisplay");

  if (!multiselect || !display) return;

  const checkboxes =
    multiselect.querySelectorAll("input[type='checkbox']");

  display.addEventListener("click", () => {
    if (multiselect.classList.contains("disabled")) return;
    multiselect.classList.toggle("open");
  });

  function updateDisplay() {
    const selected = [...checkboxes]
      .filter(cb => cb.checked)
      .map(cb => `${cb.value} ✓`);

    display.textContent = selected.length
      ? selected.join(" / ")
      : "Selecione um ou mais setores envolvidos nesta extra";

    display.classList.toggle("has-value", selected.length > 0);
  }

  checkboxes.forEach(cb =>
    cb.addEventListener("change", updateDisplay)
  );

  document.addEventListener("click", e => {
    if (!multiselect.contains(e.target)) {
      multiselect.classList.remove("open");
    }
  });

});
