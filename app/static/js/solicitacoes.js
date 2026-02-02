const tbody = document.querySelector("#funcionariosTable tbody");
const funcionariosJson = document.getElementById("funcionariosJson");
const form = document.getElementById("formSolicitacao");
const btnAddRow = document.getElementById("btnAddRow");
const turnoRadios = document.querySelectorAll(".turno-radio");

const formMode = form?.dataset.mode || "create";

/**
 * Horários padrão para DIA DE EXTRA
 */
const EXTRA_SHIFT_TIMES = {
  "1T": { start: "07:00", end: "16:00" },
  "2T": { start: "16:00", end: "01:00" },
  "3T": { start: "01:00", end: "06:00" }
};

if (formMode === "create") {
  btnAddRow.addEventListener("click", addRow);
  turnoRadios.forEach(radio =>
    radio.addEventListener("change", aplicarHorarioPorTurno)
  );
}

// ===============================
// FUNÇÕES EXISTENTES (INTACTAS)
// ===============================
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
  if (formMode !== "create") return;

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
      <input type="password" class="form-control form-control-sm signature-password mb-1">
      <button type="button" class="btn btn-sm btn-outline-success btn-sign">Confirmar</button>
    </td>
    <td><button type="button" class="btn btn-sm btn-danger">X</button></td>
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

function atualizarIndices() {
  [...tbody.children].forEach((tr, i) => {
    tr.children[0].textContent = i + 1;
  });
}

// ===============================
// SUBMIT (APENAS CREATE)
// ===============================
if (formMode === "create") {
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
    if (!data.success) return alert("Erro ao registrar solicitação");

    window.location.href = "/solicitacoes/abertas";
  });

  addRow(); // primeira linha
}
