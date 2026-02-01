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
