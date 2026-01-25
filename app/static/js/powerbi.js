document.getElementById("setorSelect").addEventListener("change", async e => {
  const setor = e.target.value;
  const linhaSelect = document.getElementById("linhaSelect");

  linhaSelect.innerHTML = "<option>Todas</option>";

  if (setor === "Todos") return;

  const resp = await fetch(`/api/linhas?setor=${setor}`);
  const linhas = await resp.json();

  linhas.forEach(l => {
    const opt = document.createElement("option");
    opt.textContent = l;
    linhaSelect.appendChild(opt);
  });
});

// Toggle "Ver mais" linhas no Power BI
function toggleLinhasPowerBI() {
  const extras = document.querySelectorAll(".extra-linha-powerbi");
  if (!extras.length) return;

  const btn = document.getElementById("toggleLinhasPowerBIBtn");
  const isHidden = extras[0].classList.contains("d-none");

  extras.forEach(el => el.classList.toggle("d-none", !isHidden));
  btn.textContent = isHidden ? "Recolher" : "Ver mais";
}

// Abrir modal de faltas por linha (mesma função do dashboard)
/* ===== LINHAS POR SETOR ===== */
const linhas = {
  IM:["IM-01","IM-02"],
  PA:["PA-01","PA-02"],
  SMT:["SMT-01","SMT-02"],
  PTH:["PTH-01"]
};

async function abrirModalLinha(linha) {

  // Pegando os valores dos selects diretamente do DOM
  const data_inicial = document.querySelector("input[name='data_inicial']").value;
  const data_final   = document.querySelector("input[name='data_final']").value;
  const turno        = document.querySelector("select[name='turno']").value;
  const filial       = document.querySelector("select[name='filial']").value;

  const params = new URLSearchParams({
    linha,
    data_inicial,
    data_final,
    turno,
    filial
  });

  const resp = await fetch(`/api/dashboard/linha/cargos?${params}`);
  const dados = await resp.json();

  const lista = document.getElementById("modalLista");
  const totalSpan = document.getElementById("modalTotal");

  lista.innerHTML = "";
  let total = 0;

  if (!dados.length) {
    lista.innerHTML = `<li class="list-group-item text-muted">Nenhuma falta registrada</li>`;
  }

  dados.forEach(c => {
    total += c.total;
    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        ${c.nome}
        <span class="badge bg-danger">${c.total}</span>
      </li>`;
  });

  totalSpan.innerText = total;

  new bootstrap.Modal(document.getElementById("modalLinha")).show();
}
