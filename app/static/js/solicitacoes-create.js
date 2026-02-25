document.addEventListener("DOMContentLoaded", () => {

  const form = document.getElementById("formSolicitacao");
  const btnAddRow = document.getElementById("btnAddRow");
  const tbody = document.querySelector("#funcionariosTable tbody");
  const funcionariosJson = document.getElementById("funcionariosJson");
  const turnoSelect = document.querySelector(".turno-select");


  if (!form || !btnAddRow || !tbody) return;

  const loggedUserMatricula = form.dataset.userMatricula;

  if (!loggedUserMatricula) {
    console.warn("Matrícula do usuário logado não encontrada");
  }

  const EXTRA_SHIFT_TIMES = {
    "1T": { start: "07:00", end: "16:00" },
    "2T": { start: "16:00", end: "01:00" },
    "3T": { start: "01:00", end: "06:00" }
  };

  btnAddRow.addEventListener("click", addRow);

  if (turnoSelect) {
    turnoSelect.addEventListener("change", aplicarHorarioPorTurno);
  }

  addRow();

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

  document.querySelectorAll(".btn-approve").forEach(button => {
    button.addEventListener("click", async () => {
      const container = button.closest(".approval-item");
      const inputWrapper =
        container.querySelector(".approval-input-wrapper");
      const passwordInput =
        container.querySelector(".approval-password");

      if (!passwordInput) return;

      const password = passwordInput.value.trim();

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

      inputWrapper.innerHTML = `
        <div class="approval-box signed">
          ${data.username}
        </div>
      `;

      button.remove();
    });
  });

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

    row.querySelector(".btn-sign")
      .addEventListener("click", () =>
        confirmarAssinaturaFuncionario(row)
      );
  }

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

  async function buscarFuncionario(row) {
    const matricula = row.querySelector(".matricula").value.trim();
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

  function aplicarHorarioPorTurno() {
    const turnoSelect = document.querySelector(".turno-select");
  
    if (!turnoSelect || !turnoSelect.value) return;
  
    const horarios = EXTRA_SHIFT_TIMES[turnoSelect.value];
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
