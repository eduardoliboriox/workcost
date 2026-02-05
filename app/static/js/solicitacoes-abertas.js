document.addEventListener("DOMContentLoaded", () => {

  const searchInput = document.getElementById("filterSearch");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");
  const estadoSelect = document.getElementById("filterEstado");
  const rows = document.querySelectorAll("tbody tr");

  if (!searchInput || !startDateInput || !endDateInput || !estadoSelect) return;

  const today = new Date();
  const currentYear = today.getFullYear();

  startDateInput.value = `${currentYear}-01-01`;
  endDateInput.value = today.toISOString().split("T")[0];

  searchInput.addEventListener("input", applyFilters);
  startDateInput.addEventListener("change", applyFilters);
  endDateInput.addEventListener("change", applyFilters);
  estadoSelect.addEventListener("change", applyFilters);

  function getEstadoAtual(row) {
    const cells = row.querySelectorAll("td");

    const solicitacaoStatus = cells[4].innerText.toLowerCase();
    if (solicitacaoStatus.includes("pendente")) {
      return "solicitante";
    }

    const roles = ["gestor", "gerente", "controladoria", "diretoria", "rh"];

    for (let i = 0; i < roles.length; i++) {
      const cellText = cells[5 + i].innerText.toLowerCase();
      if (cellText.includes("pendente")) {
        return roles[i];
      }
    }

    return "concluida";
  }

  function applyFilters() {
    const search = searchInput.value.toLowerCase().trim();
    const startDate = new Date(startDateInput.value);
    const endDate = new Date(endDateInput.value);
    const estado = estadoSelect.value;

    rows.forEach(row => {
      const text = row.innerText.toLowerCase();

      const dateCell = row.querySelector("td:nth-child(2)");
      if (!dateCell) return;

      const [day, month, year] = dateCell.innerText.split("/");
      const rowDate = new Date(`${year}-${month}-${day}`);

      const matchesText = !search || text.includes(search);
      const matchesDate =
        (!startDateInput.value || rowDate >= startDate) &&
        (!endDateInput.value || rowDate <= endDate);

      const estadoAtual = getEstadoAtual(row);
      const matchesEstado = !estado || estadoAtual === estado;

      row.style.display =
        matchesText && matchesDate && matchesEstado ? "" : "none";
    });
  }

});
