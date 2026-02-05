document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  const pendingApprovals = [];

  /* ============================
     APROVAÇÃO (VIEW)
     ============================ */
  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async (e) => {
      e.preventDefault();

      const role = item.dataset.role?.toLowerCase();
      const passwordInput = item.querySelector(".approval-password");
      const password = passwordInput?.value?.trim();

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

      let usernameDiv = box.querySelector(".approval-username");
      if (!usernameDiv) {
        usernameDiv = document.createElement("div");
        usernameDiv.className = "approval-username";
        box.appendChild(usernameDiv);
      }

      usernameDiv.textContent = data.username;
    });
  });

  /* ============================
     FUNCIONÁRIOS (VIEW) — FIX DEFINITIVO
     ============================ */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-sign");
    if (!btn) return;

    e.preventDefault();

    const row = btn.closest("tr");

    // ✅ FIX REAL: usar VALUE, não dataset
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

    const box = row.querySelector(".signature-box");
    box.classList.remove("pending");
    box.classList.add("signed");
    box.textContent = data.username;

    row.querySelector(".signature-password")?.remove();
    btn.remove();
  });

  /* ============================
     SALVAR VIEW (somente aprovações)
     ============================ */
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
