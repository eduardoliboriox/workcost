document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll(".btn-details").forEach(btn => {
    btn.addEventListener("click", () => {
      const id = btn.dataset.id;
      alert(
        `Detalhes da solicitação ${id}\n\n` +
        "Abertura de mini modal aqui (próximo passo)"
      );
    });
  });

});
