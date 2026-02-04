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

    const matricula =
      String(matriculaInput?.dataset?.matricula || "").trim();
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

  /* ======================================================
     FLUXO DE APROVAÇÃO — VIEW
     ====================================================== */
  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async () => {
      const role = item.dataset.role;
      const passwordInput = item.querySelector(".approval-password");
      const password = passwordInput?.value?.trim();

      if (!role || !password) {
        alert("Informe a senha");
        return;
      }

      try {
        const authRes = await fetch("/api/auth/confirm-extra", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            matricula: form.dataset.userMatricula,
            password
          })
        });

        const authData = await parseJsonSafe(authRes);

        if (!authRes.ok || !authData?.success) {
          alert(authData?.error || "Senha inválida");
          return;
        }

        const res = await fetch(
          `/api/solicitacoes/${solicitacaoId}/aprovar`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ role })
          }
        );

        if (!res.ok) {
          alert("Erro ao registrar aprovação");
          return;
        }

        item.querySelector(".approval-input-wrapper").innerHTML = `
          <div class="approval-box signed">
            ${authData.username}
          </div>
        `;

        btn.remove();

      } catch (err) {
        console.error(err);
        alert("Erro no fluxo de aprovação");
      }
    });
  });
});
