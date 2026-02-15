document.addEventListener("DOMContentLoaded", function () {

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
