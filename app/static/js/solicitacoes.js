let funcionarios = [];
const tbody = document.querySelector("#funcionariosTable tbody");

function addFuncionario(){

  const idx = funcionarios.length;

  funcionarios.push({
    matricula:"",
    nome:"",
    endereco:"",
    telefone:"",
    inicio:"",
    termino:"",
    transporte:"ROTA"
  });

  render();
}

function render(){
  tbody.innerHTML = "";

  funcionarios.forEach((f,i)=>{

    tbody.innerHTML += `
    <tr>
      <td>${i+1}</td>
      <td><input class="form-control" onchange="setVal(${i},'matricula',this.value)"></td>
      <td><input class="form-control" onchange="setVal(${i},'nome',this.value)"></td>
      <td><input class="form-control" onchange="setVal(${i},'endereco',this.value)"></td>
      <td><input class="form-control" onchange="setVal(${i},'telefone',this.value)"></td>
      <td><input type="time" class="form-control" onchange="setVal(${i},'inicio',this.value)"></td>
      <td><input type="time" class="form-control" onchange="setVal(${i},'termino',this.value)"></td>
      <td>
        <select class="form-select" onchange="setVal(${i},'transporte',this.value)">
          <option>ROTA</option>
          <option>VEÍCULO PRÓPRIO</option>
        </select>
      </td>
      <td><button onclick="removeFuncionario(${i})" class="btn btn-sm btn-danger">x</button></td>
    </tr>
    `;
  });

  document.getElementById("funcionariosJson").value = JSON.stringify(funcionarios);
}

function setVal(i,k,v){
  funcionarios[i][k]=v;
  document.getElementById("funcionariosJson").value = JSON.stringify(funcionarios);
}

function removeFuncionario(i){
  funcionarios.splice(i,1);
  render();
}


const tbody = document.querySelector("#funcionariosTable tbody");
const funcionariosJson = document.getElementById("funcionariosJson");
const form = document.getElementById("formSolicitacao");


/* ===============================
   ADD ROW
================================ */
function addFuncionario() {
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
                <option value="Rota">Rota</option>
                <option value="Veículo próprio">Veículo próprio</option>
            </select>
        </td>
        <td>
            <button class="btn btn-sm btn-danger">X</button>
        </td>
    `;

    tbody.appendChild(row);

    atualizarIndex(row);
    bindRowEvents(row);
}


/* ===============================
   EVENTS
================================ */
function bindRowEvents(row) {

    const matriculaInput = row.querySelector(".matricula");
    const deleteBtn = row.querySelector("button");

    matriculaInput.addEventListener("blur", () => buscarFuncionario(row));
    deleteBtn.addEventListener("click", () => row.remove());
}


/* ===============================
   FETCH API
================================ */
async function buscarFuncionario(row) {

    const matricula = row.querySelector(".matricula").value;

    if (!matricula) return;

    const res = await fetch(`/api/employees/${matricula}`);
    const data = await res.json();

    if (!data.found) return;

    row.querySelector(".nome").value = data.nome;
    row.querySelector(".telefone").value = data.telefone || "";
    row.querySelector(".endereco").value = data.endereco || "";
}


/* ===============================
   SUBMIT
================================ */
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


/* ===============================
   UTILS
================================ */
function atualizarIndex(row) {
    row.children[0].textContent = tbody.children.length;
}


addFuncionario();

