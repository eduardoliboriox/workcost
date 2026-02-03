document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("formSolicitacao");
  const solicitacaoId = form?.dataset.solicitacaoId;

  if (!form || !solicitacaoId) return;

  document.querySelectorAll(".btn-sign").forEach(button => {
    button.addEventListener("click", async () => {
      const row = button.closest("tr");
      const cell = button.closest("td");

      const matricula =
        row.querySelector(".matricula")?.dataset.matricula;

      const passwordInput =
        cell.querySelector(".signature-password");

      const password = passwordInput?.value?.trim();
      const box = cell.querySelector(".signature-box");

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

      box.textContent = data.username;
      box.classList.remove("pending");
      box.classList.add("signed");

      passwordInput.remove();
      button.remove();
    });
  });
});
