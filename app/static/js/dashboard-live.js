let dashboardIsLoading = false;
let dashboardTimeout = null;

/* ======================================================
   CACHE LOCAL ABSENTEÍSMO (ISOLADO)
   ====================================================== */
let cacheAbsenteismoData = [];

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

    const responses = await Promise.all([
      fetch(`/api/dashboard/resumo?${params}`),
      fetch(`/api/dashboard/solicitacoes-resumo?${params}`),
      fetch(`/api/dashboard/extras?${params}`),
      fetch(`/api/dashboard/objetivos?${params}`),
      fetch(`/api/dashboard/clientes?${params}`),
      fetch(`/api/dashboard/tipos-solicitacao?${params}`),
      fetch(`/api/dashboard/absenteismo-por-data?${params}`)
    ]);

    const [
      dataResumo,
      dataSolicitacoes,
      rankingExtras,
      rankingObjetivos,
      rankingClientes,
      rankingTipos,
      rankingAbsData
    ] = await Promise.all(responses.map(r => r.json()));

    /* 🔥 salva cache sem afetar nada */
    cacheAbsenteismoData = rankingAbsData || [];

    // ===============================
    // KPIs (INALTERADO)
    // ===============================
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

/* ======================================================
   ABSENTEÍSMO POR DATA (INALTERADO)
   ====================================================== */

function atualizarAbsenteismoPorData(dados) {

  const lista = document.getElementById("rankingAbsenteismoDataList");
  const btn = document.getElementById("toggleDatasBtn");

  if (!lista) return;

  lista.innerHTML = "";

  dados.forEach((d, index) => {

    const dataFormatada =
      new Date(d.data).toLocaleDateString("pt-BR");

    lista.innerHTML += `
      <li class="list-group-item d-flex justify-content-between
          ${index >= 5 ? 'd-none extra-data' : ''}"
          style="cursor:pointer"
          onclick="abrirModalAbsenteismo('${d.data}')">
        <span>${dataFormatada}</span>
        <span class="badge bg-danger">${d.qtd}</span>
      </li>
    `;
  });

  if (btn) {
    if (dados.length > 5) {
      btn.classList.remove("d-none");
      btn.innerText = "Ver mais";
    } else {
      btn.classList.add("d-none");
    }
  }
}

/* ======================================================
   🔥 MINI MODAL ABSENTEÍSMO (NOVO)
   ====================================================== */

function abrirModalAbsenteismo(data) {

  const registro =
    cacheAbsenteismoData.find(d => d.data === data);

  if (!registro) return;

  const titulo =
    document.getElementById("modalAbsDataTitulo");

  const lista =
    document.getElementById("modalAbsLista");

  const totalSpan =
    document.getElementById("modalAbsTotal");

  const dataFormatada =
    new Date(data).toLocaleDateString("pt-BR");

  titulo.innerText =
    `Absenteísmo — ${dataFormatada}`;

  lista.innerHTML = "";

  let total = 0;

  if (!registro.funcionarios?.length) {

    lista.innerHTML = `
      <li class="list-group-item text-muted">
        Nenhuma falta registrada
      </li>
    `;

  } else {

    registro.funcionarios.forEach(f => {

      total += f.total;

      lista.innerHTML += `
        <li class="list-group-item d-flex justify-content-between">
          <div>
            <div class="fw-semibold">${f.nome}</div>
            <small class="text-muted">
              Matrícula: ${f.matricula}
            </small>
          </div>
          <span class="badge bg-danger">
            ${f.total}
          </span>
        </li>
      `;
    });
  }

  totalSpan.innerText = total;

  new bootstrap.Modal(
    document.getElementById("modalAbsenteismo")
  ).show();
}

document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("dashboardFilters");
  if (!form) return;

  form.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("change", () => {
      debounceDashboardUpdate(() => atualizarDashboard());
    });
  });

  atualizarDashboard();
});

setInterval(() => {
  if (!dashboardIsLoading) {
    atualizarDashboard();
  }
}, 10000);