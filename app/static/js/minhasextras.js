document.addEventListener("DOMContentLoaded", () => {

  const tableRows = document.querySelectorAll("tbody tr");
  const mobileCards = document.querySelectorAll(".solicitacao-card");

  const searchInput = document.getElementById("filterSearch");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");

  if (!searchInput || !startDateInput || !endDateInput) return;

  function parseDate(text) {
    if (!text) return null;
    const [day, month, year] = text.trim().split("/");
    return new Date(`${year}-${month}-${day}`);
  }

  function applyFilters() {
    const search = searchInput.value.toLowerCase().trim();
    const startDate = startDateInput.value
      ? new Date(startDateInput.value)
      : null;
    const endDate = endDateInput.value
      ? new Date(endDateInput.value)
      : null;

    /* =====================
       DESKTOP (tabela)
       ===================== */
    tableRows.forEach(row => {
      const text = row.innerText.toLowerCase();
      const dateCell = row.querySelector("td:nth-child(2)");
      const rowDate = parseDate(dateCell?.innerText);

      const matchesText = !search || text.includes(search);
      const matchesDate =
        (!startDate || (rowDate && rowDate >= startDate)) &&
        (!endDate || (rowDate && rowDate <= endDate));

      row.style.display =
        matchesText && matchesDate ? "" : "none";
    });

    /* =====================
       MOBILE (cards)
       ===================== */
    mobileCards.forEach(card => {
      const text = card.innerText.toLowerCase();

      const dataText =
        card.querySelector(".card-content div:nth-child(1)")?.innerText;
      const cardDate = dataText
        ? parseDate(dataText.split(":")[1])
        : null;

      const matchesText = !search || text.includes(search);
      const matchesDate =
        (!startDate || (cardDate && cardDate >= startDate)) &&
        (!endDate || (cardDate && cardDate <= endDate));

      card.style.display =
        matchesText && matchesDate ? "" : "none";
    });
  }

  [searchInput, startDateInput, endDateInput]
    .forEach(el => el.addEventListener("input", applyFilters));

});
