document.addEventListener("DOMContentLoaded", () => {

  const modalEl = document.getElementById("modalSolicitacaoMobile");
  if (!modalEl) return;

  const modal = new bootstrap.Modal(modalEl);

  document.querySelectorAll(".btn-details").forEach(btn => {
    btn.addEventListener("click", () => {
      const card = btn.closest(".solicitacao-card");

      const id = card.dataset.id;
      const status = card.querySelector(".badge").innerText;
      const body = card.querySelector(".card-body").innerHTML;

      document.getElementById("modalSolicitacaoId").innerText = `#${id}`;

      document.getElementById("modalSolicitacaoBody").innerHTML = `
        <div class="mb-2"><strong>Status:</strong> ${status}</div>
        ${body}
        <hr>
        <div class="text-muted small">
          Gestor, Gerente, Controladoria, Diretoria e RH
          são exibidos aqui futuramente sem alterar backend.
        </div>
      `;

      modal.show();
    });
  });

});
