document.addEventListener("DOMContentLoaded", () => {

  /* ======================================================
     ELEMENTOS PRINCIPAIS DA PÁGINA (MODO CREATE)
     ====================================================== */

  const form = document.getElementById("formSolicitacao");
  const btnAddRow = document.getElementById("btnAddRow");
  const tbody = document.querySelector("#funcionariosTable tbody");
  const funcionariosJson = document.getElementById("funcionariosJson");
  const turnoRadios = document.querySelectorAll(".turno-radio");

  // Se não estiver na página correta, aborta
  if (!form || !btnAddRow || !tbody) return;

  /* ======================================================
     MATRÍCULA DO USUÁRIO LOGADO
     Usada EXCLUSIVAMENTE no Fluxo de Aprovação (create)
     ====================================================== */

  const loggedUserMatricula = form.dataset.userMatricula;

  if (!loggedUserMatricula) {
    console.warn(
      "⚠️ Matrícula do usuário logado não encontrada (data-user-matricula)"
    );
  }

  /* ======================================================
     HORÁRIOS PADRÃO POR TURNO (DIA DE EXTRA)
     ====================================================== */

  const EXTRA_SHIFT_TIMES = {
    "1T": { start: "07:00", end: "16:00" },
    "2T": { start: "16:00", end: "01:00" },
    "3T": { start: "01:00", end: "06:00" }
  };

  btnAddRow.addEventListener("click", addRow);

  turnoRadios.forEach(radio =>
    radio.addEventListener("change", aplicarHorarioPorTurno)
  );

  // Primeira linha sempre criada no modo create
  addRow();

  /* ======================================================
     SUBMIT DO FORMULÁRIO (CRIAR SOLICITAÇÃO)
     ====================================================== */

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const rows = [...tbody.querySelectorAll("tr")];

    const funcionarios = rows.map(r => ({
      matricula: r.querySelector(".matricula").value,
      nome: r.querySelector(".nome").value,
      endereco: r.querySelector(".endereco").value,
      telefone: r.querySelector(".telefone").value,
      inicio: r.querySelector(".inicio").value,
      termino: r.querySelector(".termino").value,
      transporte: r.querySelector(".transporte").value
    }));

    funcionariosJson.value = JSON.stringify(funcionarios);

    const res = await fetch("/api/solicitacoes", {
      method: "POST",
      body: new FormData(form)
    });

    const data = await res.json();

    if (!data.success) {
      alert("Erro ao registrar solicitação");
      return;
    }

    window.location.href = "/solicitacoes/abertas";
  });

  /* ======================================================
     FLUXO DE APROVAÇÃO — MODO CREATE
     - Usa usuário LOGADO
     - NÃO grava no banco
     - Apenas valida senha
     ====================================================== */

  document.querySelectorAll(".btn-approve").forEach(button => {
    button.addEventListener("click", async () => {
      const container = button.closest(".approval-item");
      const passwordInput =
        container.querySelector(".approval-password");
      const box =
        container.querySelector(".approval-box");

      // Evita dupla assinatura
      if (box.classList.contains("signed")) return;

      const password = passwordInput?.value?.trim();

      if (!password) {
        alert("Informe a senha");
        return;
      }

      const res = await fetch("/api/auth/confirm-extra", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          matricula: loggedUserMatricula,
          password
        })
      });

      const data = await res.json();

      if (!res.ok || !data.success) {
        alert(data.error || "Senha inválida");
        return;
      }

      // Feedback visual conforme regra de negócio
      box.textContent = data.username;
      box.classList.remove("pending");
      box.classList.add("signed");

      passwordInput.remove();
      button.remove();
    });
  });

  /* ======================================================
     MANIPULAÇÃO DAS LINHAS DE FUNCIONÁRIOS
     ====================================================== */

  function addRow() {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td></td>
      <td><input class="form-control matricula"></td>
      <td><input class="form-control nome" readonly></td>
      <td><input class="form-control endereco" readonly></td>
      <td><input class="form-control telefone" readonly></td>
      <td><input type="time" class="form-control inicio"></td>
      <td><input type="time" class="form-control termino"></td>
      <td>
        <select class="form-select transporte">
          <option value="">-</option>
          <option value="ROTA">Rota</option>
          <option value="VEICULO">Veículo próprio</option>
        </select>
      </td>
      <td>
        <div class="signature-box pending mb-1">pendente</div>
        <input type="password"
               class="form-control form-control-sm signature-password mb-1"
               placeholder="Senha">
        <button type="button"
                class="btn btn-sm btn-outline-success btn-sign">
          Confirmar
        </button>
      </td>
      <td>
        <button type="button"
                class="btn btn-sm btn-danger">X</button>
      </td>
    `;

    tbody.appendChild(row);
    atualizarIndices();
    bindRow(row);
    aplicarHorarioPorTurno();
  }

  function bindRow(row) {
    row.querySelector(".matricula")
      .addEventListener("blur", () => buscarFuncionario(row));

    row.querySelector(".transporte")
      .addEventListener("change", () => aplicarTransporte(row));

    row.querySelector(".btn-danger")
      .addEventListener("click", () => {
        row.remove();
        atualizarIndices();
      });

    // Assinatura do FUNCIONÁRIO (create)
    row.querySelector(".btn-sign")
      .addEventListener("click", () =>
        confirmarAssinaturaFuncionario(row)
      );
  }

  /* ======================================================
     ASSINATURA DO FUNCIONÁRIO — MODO CREATE
     ====================================================== */

  async function confirmarAssinaturaFuncionario(row) {
    const matricula =
      row.querySelector(".matricula")?.value?.trim();

    const password =
      row.querySelector(".signature-password")?.value?.trim();

    const box = row.querySelector(".signature-box");
    const btn = row.querySelector(".btn-sign");
    const input = row.querySelector(".signature-password");

    if (!matricula || !password) {
      alert("Informe matrícula e senha");
      return;
    }

    const res = await fetch("/api/auth/confirm-extra", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ matricula, password })
    });

    const data = await res.json();

    if (!res.ok || !data.success) {
      alert(data.error || "Senha inválida");
      return;
    }

    box.textContent = data.username;
    box.classList.remove("pending");
    box.classList.add("signed");

    input.remove();
    btn.remove();
  }

  /* ======================================================
     AUTO-PREENCHIMENTO DO FUNCIONÁRIO
     ====================================================== */

  async function buscarFuncionario(row) {
    const matricula =
      row.querySelector(".matricula").value.trim();

    if (!matricula) return;

    const res = await fetch(`/api/employees/${matricula}`);
    const data = await res.json();

    if (!data.found) return;

    row.querySelector(".nome").value = data.nome;
    row.querySelector(".telefone").value = data.telefone || "";
    row.querySelector(".endereco").value = data.endereco || "";
  }

  function aplicarTransporte(row) {
    if (row.querySelector(".transporte").value === "VEICULO") {
      row.querySelector(".endereco").value = "Veículo próprio";
    }
  }

  /* ======================================================
     TURNO → HORÁRIO AUTOMÁTICO
     ====================================================== */

  function aplicarHorarioPorTurno() {
    const turnoSelecionado =
      document.querySelector(".turno-radio:checked");

    if (!turnoSelecionado) return;

    const horarios =
      EXTRA_SHIFT_TIMES[turnoSelecionado.value];

    if (!horarios) return;

    [...tbody.querySelectorAll("tr")].forEach(row => {
      row.querySelector(".inicio").value = horarios.start;
      row.querySelector(".termino").value = horarios.end;
    });
  }

  function atualizarIndices() {
    [...tbody.children].forEach((tr, i) => {
      tr.children[0].textContent = i + 1;
    });
  }

});
