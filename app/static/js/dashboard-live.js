async function atualizarDashboard() {
  try {
    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value || '',
      filial: document.querySelector('[name="filial"]').value || ''
    });

    const respResumo = await fetch(`/api/dashboard/resumo?${params}`);
    const dataResumo = await respResumo.json();

    document.getElementById("kpi-abs").innerText =
      dataResumo.kpis.absenteismo + "%";

    document.getElementById("kpi-linhas").innerText =
      dataResumo.kpis.linhas;                                         

    const respSolicitacoes = await fetch(`/api/dashboard/solicitacoes-resumo?${params}`);
    const dataSolicitacoes = await respSolicitacoes.json();
    
    document.getElementById("kpi-solicitacoes-abertas").innerText =
      dataSolicitacoes.abertas;
    
    document.getElementById("kpi-solicitacoes-fechadas").innerText =
      dataSolicitacoes.fechadas;
    
    document.getElementById("kpi-total-gasto").innerText =
      "R$ " + dataSolicitacoes.total_gasto
        .toFixed(2)
        .replace(".", ",");

    // Extras
    const respExtras = await fetch(`/api/dashboard/extras?${params}`);
    const rankingExtras = await respExtras.json();
    atualizarTabelaExtras(rankingExtras);

    // Objetivos
    const respObjetivos = await fetch(`/api/dashboard/objetivos?${params}`);
    const rankingObjetivos = await respObjetivos.json();
    atualizarObjetivos(rankingObjetivos);

    // Clientes
    const respClientes = await fetch(`/api/dashboard/clientes?${params}`);
    const rankingClientes = await respClientes.json();
    atualizarClientes(rankingClientes);
        
    // Tipos de Solicitação
    const respTipos = await fetch(`/api/dashboard/tipos-solicitacao?${params}`);
    const rankingTipos = await respTipos.json();
    atualizarTipos(rankingTipos);

  } catch (e) {
    console.error("Erro ao atualizar dashboard", e);
  }
}

function atualizarClientes(dados) {
  const lista = document.getElementById("rankingClientesList");
  if (!lista) return;

  lista.innerHTML = "";

  dados.forEach(c => {
    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        ${c.cliente}
        <span class="badge bg-warning">${c.percentual}%</span>
      </li>
    `;
  });
}

function atualizarTabelaExtras(dados) {
  const tbody = document.querySelector("#rankingExtrasBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  dados.forEach(f => {
    tbody.innerHTML += `
      <tr>
        <td class="fw-semibold">${f.filial}</td>
        <td><span class="badge bg-primary">${f.percentual}%</span></td>
        <td class="text-warning fw-bold">R$ ${f.provisionado.toFixed(2)}</td>
        <td class="text-success fw-bold">R$ ${f.realizado.toFixed(2)}</td>
      </tr>
    `;
  });
}

function atualizarObjetivos(dados) {
  const lista = document.getElementById("rankingObjetivosList");
  if (!lista) return;

  lista.innerHTML = "";

  dados.forEach(o => {
    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        ${o.status}
        <span class="badge bg-danger">${o.percentual}%</span>
      </li>
    `;
  });
}

function atualizarTipos(dados) {
  const lista = document.getElementById("rankingTiposList");
  if (!lista) return;

  lista.innerHTML = "";

  dados.forEach(t => {
    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        ${t.tipo}
        <span class="badge bg-info">${t.percentual}%</span>
      </li>
    `;
  });
}

document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("dashboardFilters");
  if (!form) return;

  form.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("change", () => {
      atualizarDashboard();
    });
  });

  atualizarDashboard();
});

setInterval(atualizarDashboard, 5000);
