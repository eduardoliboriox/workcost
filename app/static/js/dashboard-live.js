async function atualizarDashboard() {
  try {
    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value || '',
      filial: document.querySelector('[name="filial"]').value || ''
    });

    // KPIs
    const respResumo = await fetch(`/api/dashboard/resumo?${params}`);
    const dataResumo = await respResumo.json();

    document.getElementById("kpi-hc-planejado").innerText = dataResumo.kpis.hc_planejado;
    document.getElementById("kpi-hc-real").innerText = dataResumo.kpis.hc_real;
    document.getElementById("kpi-ausencias").innerText = dataResumo.kpis.ausencias;
    document.getElementById("kpi-abs").innerText = dataResumo.kpis.absenteismo + "%";
    document.getElementById("kpi-linhas").innerText = dataResumo.kpis.linhas;

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
