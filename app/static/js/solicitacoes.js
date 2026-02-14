document.addEventListener("DOMContentLoaded", () => {

  function initMultiselect(containerId, displayId, emptyText) {

    const multiselect = document.getElementById(containerId);
    const display = document.getElementById(displayId);

    if (!multiselect || !display) return;

    const checkboxes =
      multiselect.querySelectorAll("input[type='checkbox']");

    display.addEventListener("click", (e) => {
      e.stopPropagation();
      if (multiselect.classList.contains("disabled")) return;
      multiselect.classList.toggle("open");
    });

    function updateDisplay() {
      const selected = [...checkboxes]
        .filter(cb => cb.checked)
        .map(cb => `${cb.value} ✓`);

      display.textContent = selected.length
        ? selected.join(" / ")
        : emptyText;

      display.classList.toggle("has-value", selected.length > 0);
    }

    checkboxes.forEach(cb =>
      cb.addEventListener("change", updateDisplay)
    );

    document.addEventListener("click", (e) => {
      if (!multiselect.contains(e.target)) {
        multiselect.classList.remove("open");
      }
    });

    updateDisplay();
  }

  initMultiselect(
    "setoresSelect",
    "setoresDisplay",
    "Selecione um ou mais setores envolvidos nesta extra"
  );

  // CLIENTES
  initMultiselect(
    "clientesSelect",
    "clientesDisplay",
    "Selecione um ou mais clientes"
  );

});
