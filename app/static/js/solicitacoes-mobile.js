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

});
