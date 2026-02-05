document.addEventListener("DOMContentLoaded", () => {

  /* ======================================================
     ELEMENTOS BASE
     ====================================================== */

  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  const pendingApprovals = [];
  const signedEmployees = [];   // ✅ NOVO ESTADO LOCAL

  /* ======================================================
     FLUXO DE APROVAÇÃO (VIEW) — JÁ FUNCIONAVA
     ====================================================== */

  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async (e) => {
      e.preventDefault();

      const role = item.dataset.role?.toLowerCase();
      const password = item.querySelector(".approval-password")?.value?.trim();

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
     FUNCIONÁRIOS — ASSINATURA (VIEW) ✅ FIX FINAL
     ====================================================== */

  document.querySelectorAll("#funcionariosTable .btn-sign")
    .forEach(btn => {

      btn.addEventListener("click", async (e) => {
        e.preventDefault();

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

        // ✅ Atualiza UI
        const box = row.querySelector(".signature-box");
        box.textContent = data.username;
        box.classList.replace("pending", "signed");

        row.querySelector(".signature-password")?.remove();
        btn.remove();

        // ✅ Atualiza estado local
        signedEmployees.push({
          matricula,
          username: data.username
        });
      });
    });

  /* ======================================================
     SALVAR VIEW (aprovações + funcionários)
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
            aprovacoes: pendingApprovals,
            funcionarios: signedEmployees   // ✅ AGORA ENVIADO
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
