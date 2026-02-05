document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  const pendingApprovals = [];
  const pendingEmployees = [];

  /* ============================
     APROVAÇÃO (VIEW)
     ============================ */
  document.querySelectorAll(".approval-item").forEach(item => {
    const btn = item.querySelector(".btn-approve");
    if (!btn) return;

    btn.addEventListener("click", async () => {
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

      item.querySelector(".approval-box")
        .classList.replace("pending", "signed");

      item.querySelector(".approval-box").textContent =
        data.username;
    });
  });

  /* ============================
     FUNCIONÁRIOS (VIEW)
     ============================ */
  document.addEventListener("click", async (e) => {
    const btn = e.target.closest(".btn-sign");
    if (!btn) return;

    const row = btn.closest("tr");

    let matricula =
      row.querySelector(".matricula")?.dataset?.matricula;

    const password =
      row.querySelector(".signature-password")?.value?.trim();

    if (!matricula || !password) return;

    // 🔐 NORMALIZAÇÃO DEFENSIVA
    matricula = matricula.trim().replace(/^0+/, "");

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

    pendingEmployees.push({
      matricula,
      username: data.username
    });

    row.querySelector(".signature-box")
      .classList.replace("pending", "signed");

    row.querySelector(".signature-box").textContent =
      data.username;

    row.querySelector(".signature-password").remove();
    btn.remove();
  });

  /* ============================
     SALVAR VIEW
     ============================ */
  document.getElementById("btnSaveView")
    ?.addEventListener("click", async () => {

    const res = await fetch(
      `/api/solicitacoes/${solicitacaoId}/salvar-view`,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          aprovacoes: pendingApprovals,
          funcionarios: pendingEmployees
        })
      }
    );

    if (!res.ok) {
      alert("Erro ao salvar");
      return;
    }

    // 🔁 força renderização baseada no banco
    window.location.href = `/solicitacoes/${solicitacaoId}`;
  });
});
