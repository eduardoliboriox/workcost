document.addEventListener("DOMContentLoaded", function () {

  const searchInput = document.getElementById("filterSearch");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");
  const rows = document.querySelectorAll("tbody tr");

  if (startDateInput && endDateInput) {

    const today = new Date();
    const currentYear = today.getFullYear();

    startDateInput.value = `${currentYear}-01-01`;

    endDateInput.value = today.toISOString().split("T")[0];
  }

  function applyFilters() {

    const search = searchInput?.value.toLowerCase().trim() || "";
    const startDate = startDateInput?.value
      ? new Date(startDateInput.value)
      : null;
    const endDate = endDateInput?.value
      ? new Date(endDateInput.value)
      : null;

    rows.forEach(row => {

      const text = row.innerText.toLowerCase();

      const dateCell = row.querySelector("td:nth-child(2)");
      if (!dateCell) return;

      const [day, month, year] = dateCell.innerText.split("/");
      const rowDate = new Date(`${year}-${month}-${day}`);

      const matchesText = !search || text.includes(search);

      const matchesDate =
        (!startDate || rowDate >= startDate) &&
        (!endDate || rowDate <= endDate);

      row.style.display =
        matchesText && matchesDate ? "" : "none";
    });
  }

  searchInput?.addEventListener("input", applyFilters);
  startDateInput?.addEventListener("change", applyFilters);
  endDateInput?.addEventListener("change", applyFilters);

  applyFilters();

  document.querySelectorAll(".select-acessar-fechadas")
    .forEach(select => {

      select.addEventListener("change", function () {

        const selected = this.value;
        if (!selected) return;

        const url = this.dataset[selected];

        if (url) {
          window.location.href = url;
        }

        this.value = "";
      });

    });

  async function salvarFechamento(id) {

    const objetivo = document.querySelector(
      `.objetivo-select[data-id='${id}']`
    )?.value || null;

    const observacoes = document.querySelector(
      `.observacao-input[data-id='${id}']`
    )?.value || "";

    await fetch(`/api/solicitacoes/${id}/fechamento`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        objetivo_status: objetivo,
        observacoes: observacoes
      })
    });
  }

  document.querySelectorAll(".objetivo-select")
    .forEach(select => {

      select.addEventListener("change", function () {
        const id = this.dataset.id;
        if (!id) return;
        salvarFechamento(id);
      });

    });

  document.querySelectorAll(".observacao-input")
    .forEach(input => {

      input.addEventListener("blur", function () {
        const id = this.dataset.id;
        if (!id) return;
        salvarFechamento(id);
      });

    });

});
