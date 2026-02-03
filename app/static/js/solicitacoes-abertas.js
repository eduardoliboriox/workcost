document.addEventListener("DOMContentLoaded", () => {

  /* ======================================================
     ELEMENTOS
     ====================================================== */

  const searchInput = document.getElementById("filterSearch");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");
  const rows = document.querySelectorAll("tbody tr");

  if (!searchInput || !startDateInput || !endDateInput) return;

  /* ======================================================
     DATAS PADRÃO
     ====================================================== */

  const today = new Date();
  const currentYear = today.getFullYear();

  startDateInput.value = `${currentYear}-01-01`;
  endDateInput.value = today.toISOString().split("T")[0];

  /* ======================================================
     EVENTOS
     ====================================================== */

  searchInput.addEventListener("input", applyFilters);
  startDateInput.addEventListener("change", applyFilters);
  endDateInput.addEventListener("change", applyFilters);

  /* ======================================================
     FUNÇÃO PRINCIPAL DE FILTRO
     ====================================================== */

  function applyFilters() {
    const search = searchInput.value.toLowerCase().trim();
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);

    rows.forEach(row => {
      const text = row.innerText.toLowerCase();

      const dateCell = row.querySelector("td:nth-child(2)");
      if (!dateCell) return;

      const [day, month, year] = dateCell.innerText.split("/");
      const rowDate = new Date(`${year}-${month}-${day}`);

      const matchesText =
        !search || text.includes(search);

      const matchesDate =
        (!startDateInput.value || rowDate >= startDate) &&
        (!endDateInput.value || rowDate <= endDate);

      row.style.display =
        matchesText && matchesDate ? "" : "none";
    });
  }

});
