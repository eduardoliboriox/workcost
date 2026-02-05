document.addEventListener("DOMContentLoaded", () => {

  /* ======================================================
     ELEMENTOS BASE
     ====================================================== */

  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  /* ======================================================
     🔒 FIX CRÍTICO
     Em modo VIEW, o form NÃO pode submeter
     ====================================================== */
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    e.stopImmediatePropagation();
    return false;
  });

  const pendingApprovals = [];

  /* ======================================================
     FLUXO DE APROVAÇÃO (VIEW) — MANTIDO
     ====================================================== */

  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async (e) => {
      e.preventDefault();
      e.stopPropagation();

      const role = item.dataset.role?.toLowerCase();
      const password =
        item.querySelector(".approval-password")?.value?.trim();

      if (!password || !role) {
        alert("Informe a senha");
        return;
      }

      const res = await fetch("/api/auth/confirm-extra", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          matricula: form.dataset.userMatricula,
          password
        })
      });

      const data = await res.json();
      if (!res.ok || !data.success) {
        alert(data.error || "Senha inválida");
        return;
      }

      pendingApprovals.push({ role });

      item.querySelector(".approval-input-wrapper")?.remove();
      btn.remove();

      const box = item.querySelector(".approval-box");
      box.classList.replace("pending", "signed");

      const usernameDiv = document.createElement("div");
      usernameDiv.className = "approval-username";
      usernameDiv.textContent = data.username;
      box.appendChild(usernameDiv);
    });
  });

  /* ======================================================
     FUNCIONÁRIOS — ASSINATURA (VIEW)
     Backend é a fonte da verdade
     ====================================================== */

  document.querySelectorAll("#funcionariosTable .btn-sign")
    .forEach(btn => {

      btn.addEventListener("click", async () => {
        const row = btn.closest("tr");

        const matricula =
          row.querySelector(".matricula")?.value?.trim();

        const password =
          row.querySelector(".signature-password")?.value?.trim();

        if (!matricula || !password) {
          alert("Informe a senha");
          return;
        }

        const res = await fetch(
          `/api/solicitacoes/${solicitacaoId}/confirmar-presenca`,
          {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ matricula, password })
          }
        );

        const data = await res.json();
        if (!res.ok || !data.success) {
          alert(data.error || "Senha inválida");
          return;
        }

        // 🔑 Renderiza com base no BACKEND
        const funcionario = data.funcionario;

        row.querySelector("td:nth-child(9)").innerHTML = `
          <div class="signature-box signed">
            ${funcionario.signed_by}
          </div>
        `;
      });

    });

  /* ======================================================
     SALVAR VIEW (somente aprovações)
     ====================================================== */

  document.getElementById("btnSaveView")
    ?.addEventListener("click", async (e) => {
      e.preventDefault();

      const res = await fetch(
        `/api/solicitacoes/${solicitacaoId}/salvar-view`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            aprovacoes: pendingApprovals
          })
        }
      );

      if (!res.ok) {
        alert("Erro ao salvar");
        return;
      }

      window.location.href = `/solicitacoes/${solicitacaoId}`;
    });

});
