document.addEventListener("DOMContentLoaded", () => {

  const btn = document.getElementById("btnSalvarFrequencia");
  if (!btn) return;

  btn.addEventListener("click", async () => {

    const rows = document.querySelectorAll("tbody tr");

    const dados = [...rows].map(row => ({
      matricula: row.dataset.matricula,
      compareceu:
        row.querySelector(".presenca-select").value === "true"
    }));

    const res = await fetch(
      `/api/solicitacoes/${SOLICITACAO_ID}/frequencia`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(dados)
      }
    );

    if (!res.ok) {
      alert("Erro ao salvar frequência");
      return;
    }

    window.location.href = "/solicitacoes/fechadas";
  });

});
