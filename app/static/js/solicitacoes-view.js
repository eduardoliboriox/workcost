document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  async function parseJsonSafe(response) {
    const text = await response.text();
    if (!text) return null;
    try {
      return JSON.parse(text);
    } catch {
      return null;
    }
  }

  /* ======================================================
     ASSINATURA DE FUNCIONÁRIO — VIEW
     ====================================================== */
  document.addEventListener("click", async (event) => {
    const button = event.target.closest(".btn-sign");
    if (!button) return;

    event.preventDefault();

    const row = button.closest("tr");
    if (!row) return;

    const matriculaInput = row.querySelector(".matricula");
    const passwordInput = row.querySelector(".signature-password");
    const box = row.querySelector(".signature-box");

    // ✅ NORMALIZA MATRÍCULA (remove zeros à esquerda)
    const rawMatricula =
      String(matriculaInput?.dataset?.matricula || "").trim();

    const matricula = rawMatricula.replace(/^0+/, "");
    const password = passwordInput?.value?.trim();

    if (!matricula || !password) {
      alert("Informe a senha do funcionário");
      return;
    }

    try {
      const res = await fetch(
        `/api/solicitacoes/${solicitacaoId}/confirmar-presenca`,
        {
          method: "POST",
          credentials: "same-origin",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ matricula, password })
        }
      );

      const data = await parseJsonSafe(res);

      if (!res.ok || !data?.success) {
        alert(data?.error || "Senha inválida");
        return;
      }

      box.textContent = data.username;
      box.classList.remove("pending");
      box.classList.add("signed");

      passwordInput.remove();
      button.remove();

    } catch (err) {
      console.error(err);
      alert("Erro ao confirmar assinatura");
    }
  });

});
