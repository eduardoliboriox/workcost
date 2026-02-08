document.addEventListener("DOMContentLoaded", () => {

  const container = document.querySelector(".solicitacoes-mobile");
  if (!container) return;

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
      `;

      modal.show();
    });
  });

});
