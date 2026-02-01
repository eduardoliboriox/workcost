const tbody = document.querySelector("#funcionariosTable tbody");
const funcionariosJson = document.getElementById("funcionariosJson");
const form = document.getElementById("formSolicitacao");
const btnAddRow = document.getElementById("btnAddRow");

btnAddRow.addEventListener("click", addRow);

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
      <button type="button" class="btn btn-sm btn-danger">X</button>
    </td>
  `;

  tbody.appendChild(row);
  atualizarIndices();
  bindRow(row);
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
