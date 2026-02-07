document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("filterSearch");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");
  const rows = document.querySelectorAll("tbody tr");

  if (!searchInput || !startDateInput || !endDateInput) return;

  const today = new Date();
  startDateInput.value = `${today.getFullYear()}-01-01`;
  endDateInput.value = today.toISOString().split("T")[0];

  searchInput.addEventListener("input", applyFilters);
  startDateInput.addEventListener("change", applyFilters);
  endDateInput.addEventListener("change", applyFilters);

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

      const matchesText = !search || text.includes(search);
      const matchesDate =
        (!startDateInput.value || rowDate >= startDate) &&
        (!endDateInput.value || rowDate <= endDate);

      row.style.display = matchesText && matchesDate ? "" : "none";
    });
  }
});
