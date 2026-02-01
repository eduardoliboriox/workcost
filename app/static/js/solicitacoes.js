const tbody = document.querySelector("#funcionariosTable tbody");
const funcionariosJson = document.getElementById("funcionariosJson");
const form = document.getElementById("formSolicitacao");
const btnAddRow = document.getElementById("btnAddRow");
const turnoRadios = document.querySelectorAll(".turno-radio");

/**
 * Horários padrão para DIA DE EXTRA
 */
const EXTRA_SHIFT_TIMES = {
  "1T": { start: "07:00", end: "16:00" },
  "2T": { start: "16:00", end: "01:00" },
  "3T": { start: "01:00", end: "06:00" }
};

btnAddRow.addEventListener("click", addRow);
turnoRadios.forEach(radio =>
  radio.addEventListener("change", aplicarHorarioPorTurno)
);

function aplicarHorarioPorTurno() {
  const turnoSelecionado = document.querySelector(".turno-radio:checked");
  if (!turnoSelecionado) return;

  const horarios = EXTRA_SHIFT_TIMES[turnoSelecionado.value];
  if (!horarios) return;

  [...tbody.querySelectorAll("tr")].forEach(row => {
    row.querySelector(".inicio").value = horarios.start;
    row.querySelector(".termino").value = horarios.end;
  });
}

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

    <!-- ASSINATURA -->
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

    <!-- AÇÃO -->
    <td>
      <button type="button" class="btn btn-sm btn-danger">X</button>
    </td>
  `;

  tbody.appendChild(row);
  atualizarIndices();
  bindRow(row);
  aplicarHorarioPorTurno();
}

function bindRow(row) {
  const matricula = row.querySelector(".matricula");
  const transporte = row.querySelector(".transporte");
  const btnRemove = row.querySelector(".btn-danger");

  matricula.addEventListener("blur", () => buscarFuncionario(row));
  transporte.addEventListener("change", () => aplicarTransporte(row));
  btnRemove.addEventListener("click", () => {
    row.remove();
    atualizarIndices();
  });
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
  const transporte = row.querySelector(".transporte").value;
  const endereco = row.querySelector(".endereco");

  if (transporte === "VEICULO") {
    endereco.value = "Veículo próprio";
  }
}

function atualizarIndices() {
  [...tbody.children].forEach((tr, i) => {
    tr.children[0].textContent = i + 1;
  });
}

form.addEventListener("submit", () => {
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
});

// primeira linha
addRow();

// ===============================
// MULTISELECT SETORES (MANTIDO)
// ===============================
const multiselect = document.getElementById("setoresSelect");
const display = document.getElementById("setoresDisplay");
const options = multiselect.querySelector(".multiselect-options");
const checkboxes = multiselect.querySelectorAll("input[type='checkbox']");

display.addEventListener("click", () => {
  multiselect.classList.toggle("open");
});

function updateDisplay() {
  const selected = [...checkboxes]
    .filter(cb => cb.checked)
    .map(cb => `${cb.value} ✓`);

  if (selected.length) {
    display.textContent = selected.join(" / ");
    display.classList.add("has-value");
  } else {
    display.textContent =
      "Selecione um ou mais setores envolvidos nesta extra";
    display.classList.remove("has-value");
  }
}

checkboxes.forEach(cb =>
  cb.addEventListener("change", updateDisplay)
);

document.addEventListener("click", e => {
  if (!multiselect.contains(e.target)) {
    multiselect.classList.remove("open");
  }
});

// ===============================
// CONFIRMAÇÃO DE ASSINATURA EXTRA
// ===============================
document.addEventListener("click", async e => {
  if (!e.target.classList.contains("btn-sign")) return;

  const row = e.target.closest("tr");
  const cell = e.target.closest("td");

  const matricula = row.querySelector(".matricula").value.trim();
  const passwordInput = cell.querySelector(".signature-password");
  const password = passwordInput.value.trim();
  const box = cell.querySelector(".signature-box");

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

  if (!data.success) {
    alert("Senha inválida");
    return;
  }

  // UI FINAL
  box.textContent = data.username;
  box.classList.remove("pending");
  box.classList.add("signed");

  passwordInput.remove();
  e.target.remove();
});
