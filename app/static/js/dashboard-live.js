let dashboardIsLoading = false;
let dashboardTimeout = null;

/* =========================================================
   🔹 NOVO: armazenamento global seguro do absenteísmo
   ========================================================= */
let rankingAbsenteismoGlobal = [];

function showDashboardLoading() {
  const overlay = document.getElementById("dashboardLoadingOverlay");
  if (overlay) overlay.classList.remove("d-none");
}

function hideDashboardLoading() {
  const overlay = document.getElementById("dashboardLoadingOverlay");
  if (overlay) overlay.classList.add("d-none");
}

function debounceDashboardUpdate(callback, delay = 400) {
  clearTimeout(dashboardTimeout);
  dashboardTimeout = setTimeout(callback, delay);
}

async function atualizarDashboard() {

  if (dashboardIsLoading) return;

  dashboardIsLoading = true;
  showDashboardLoading();

  try {

    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value || '',
      filial: document.querySelector('[name="filial"]').value || ''
    });

    const [
      respResumo,
      respSolicitacoes,
      respExtras,
      respObjetivos,
      respClientes,
      respTipos,
      respAbsData
    ] = await Promise.all([
      fetch(`/api/dashboard/resumo?${params}`),
      fetch(`/api/dashboard/solicitacoes-resumo?${params}`),
      fetch(`/api/dashboard/extras?${params}`),
      fetch(`/api/dashboard/objetivos?${params}`),
      fetch(`/api/dashboard/clientes?${params}`),
      fetch(`/api/dashboard/tipos-solicitacao?${params}`),
      fetch(`/api/dashboard/absenteismo-por-data?${params}`)
    ]);

    const dataResumo = await respResumo.json();
    const dataSolicitacoes = await respSolicitacoes.json();
    const rankingExtras = await respExtras.json();
    const rankingObjetivos = await respObjetivos.json();
    const rankingClientes = await respClientes.json();
    const rankingTipos = await respTipos.json();
    const rankingAbsData = await respAbsData.json();

    /* 🔹 SALVA GLOBALMENTE */
    rankingAbsenteismoGlobal = rankingAbsData;

    document.getElementById("kpi-abs").innerText =
      dataResumo.kpis.absenteismo + "%";

    document.getElementById("kpi-linhas").innerText =
      dataResumo.kpis.linhas;

    document.getElementById("kpi-solicitacoes-abertas").innerText =
      dataSolicitacoes.abertas;

    document.getElementById("kpi-solicitacoes-fechadas").innerText =
      dataSolicitacoes.fechadas;

    document.getElementById("kpi-total-gasto").innerText =
      "R$ " + dataSolicitacoes.total_gasto
        .toFixed(2)
        .replace(".", ",");

    atualizarTabelaExtras(rankingExtras);
    atualizarObjetivos(rankingObjetivos);
    atualizarClientes(rankingClientes);
    atualizarTipos(rankingTipos);
    atualizarAbsenteismoPorData(rankingAbsData);

  } catch (e) {
    console.error("Erro ao atualizar dashboard", e);
  } finally {
    dashboardIsLoading = false;
    hideDashboardLoading();
  }
}

/* =========================================================
   🔹 NOVA FUNÇÃO — Modal Absenteísmo
   ========================================================= */
function abrirModalAbsenteismo(dataSelecionada) {

  const registro = rankingAbsenteismoGlobal.find(
    d => d.data === dataSelecionada
  );

  if (!registro) return;

  document.getElementById("modalAbsDataTitulo").innerText =
    `Absenteísmo — ${new Date(registro.data).toLocaleDateString("pt-BR")}`;

  const lista = document.getElementById("modalAbsLista");
  const totalSpan = document.getElementById("modalAbsTotal");

  lista.innerHTML = "";
  let total = 0;

  registro.funcionarios.forEach(f => {

    total += f.total;

    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        <span>
          <strong>${f.matricula}</strong> — ${f.nome}
        </span>
        <span class="badge bg-danger">${f.total}</span>
      </li>
    `;
  });

  totalSpan.innerText = total;

  new bootstrap.Modal(
    document.getElementById("modalAbsenteismo")
  ).show();
}
