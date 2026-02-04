document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  /* ======================================================
     ASSINATURA DE FUNCIONÁRIO (MODO VIEW)
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

    const matricula = matriculaInput?.dataset?.matricula;
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
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify({ matricula, password })
        }
      );

      const data = await res.json();

      if (!res.ok || !data.success) {
        alert(data.error || "Senha inválida");
        return;
      }

      box.textContent = data.username;
      box.classList.remove("pending");
      box.classList.add("signed");

      passwordInput.remove();
      button.remove();

    } catch (err) {
      console.error("Erro ao confirmar assinatura:", err);
      alert("Erro ao confirmar assinatura");
    }
  });

  /* ======================================================
     FLUXO DE APROVAÇÃO (MODO VIEW)
     ====================================================== */
  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async (event) => {
      event.preventDefault();

      const role = item.dataset.role?.toLowerCase();
      const passwordInput =
        item.querySelector(".approval-password");

      const password = passwordInput?.value?.trim();

      if (!password || !role) {
        alert("Informe a senha");
        return;
      }

      try {
        const resAuth = await fetch("/api/auth/confirm-extra", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify({
            matricula: form.dataset.userMatricula,
            password
          })
        });

        const authData = await resAuth.json();

        if (!resAuth.ok || !authData.success) {
          alert(authData.error || "Senha inválida");
          return;
        }

        const res = await fetch(
          `/api/solicitacoes/${solicitacaoId}/aprovar`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "Accept": "application/json"
            },
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
        console.error("Erro no fluxo de aprovação:", err);
        alert("Erro no fluxo de aprovação");
      }
    });
  });
});
