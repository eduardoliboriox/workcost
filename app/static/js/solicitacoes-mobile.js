document.addEventListener("DOMContentLoaded", () => {

  const container = document.querySelector(".page-pedidos .solicitacoes-mobile");
  if (!container) return;

  const modal = new bootstrap.Modal(
    document.getElementById("modalSolicitacaoMobile")
  );

  container.querySelectorAll(".btn-details").forEach(btn => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".solicitacao-card");

      document.getElementById("modalSolicitacaoId").innerText =
        `#${card.dataset.id}`;

      document.getElementById("modalSolicitacaoBody").innerHTML = `
        <p><strong>Solicitante:</strong> ${card.dataset.solicitante}</p>
        <p><strong>Gestor:</strong> ${card.dataset.gestor}</p>
        <p><strong>Gerente:</strong> ${card.dataset.gerente}</p>
        <p><strong>Controladoria:</strong> ${card.dataset.controladoria}</p>
        <p><strong>Diretoria:</strong> ${card.dataset.diretoria}</p>
        <p><strong>RH:</strong> ${card.dataset.rh}</p>
      `;

      modal.show();
    });
  });

  /* ===============================
     FILTROS MOBILE 
     =============================== */

  const searchInput = document.getElementById("filterSearch");
  const estadoSelect = document.getElementById("filterEstado");
  const startDateInput = document.getElementById("filterStartDate");
  const endDateInput = document.getElementById("filterEndDate");

  const cards = container.querySelectorAll(".solicitacao-card");

  function applyMobileFilters() {
    const search = searchInput.value.toLowerCase().trim();
    const estado = estadoSelect.value;
    const startDate = startDateInput.value
      ? new Date(startDateInput.value)
      : null;
    const endDate = endDateInput.value
      ? new Date(endDateInput.value)
      : null;

    cards.forEach(card => {
      const text = card.innerText.toLowerCase();

      const dataText =
        card.querySelector(".card-content div:nth-child(1)")?.innerText;
      let cardDate = null;

      if (dataText) {
        const [, dateStr] = dataText.split(":");
        const [day, month, year] = dateStr.trim().split("/");
        cardDate = new Date(`${year}-${month}-${day}`);
      }

      const matchesText =
        !search || text.includes(search);

      const matchesDate =
        (!startDate || (cardDate && cardDate >= startDate)) &&
        (!endDate || (cardDate && cardDate <= endDate));

      let matchesEstado = true;
      if (estado) {
        const status = card.querySelector(".badge")?.innerText.toLowerCase();
        matchesEstado =
          estado === "concluida"
            ? status === "confirmado"
            : status === "pendente";
      }

      card.style.display =
        matchesText && matchesDate && matchesEstado
          ? ""
          : "none";
    });
  }

  [searchInput, estadoSelect, startDateInput, endDateInput]
    .forEach(el => el && el.addEventListener("input", applyMobileFilters));

});
