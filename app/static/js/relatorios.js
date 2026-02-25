let faltasPorDataCache = [];
let showingAllDates = false;

function $(id) {
  return document.getElementById(id);
}

function toISODate(d) {
  const pad = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
}

function formatCurrencyBR(value) {
  const n = Number(value || 0);
  return "R$ " + n.toFixed(2).replace(".", ",");
}

function formatDateBR(iso) {
  try {
    return new Date(iso).toLocaleDateString("pt-BR");
  } catch {
    return String(iso || "");
  }
}

function setPeriodoDefault(periodo) {
  const hoje = new Date();
  let ini = null;
  let fim = null;

  if (periodo === "SEMANAL") {
    fim = new Date(hoje);
    ini = new Date(hoje);
    ini.setDate(ini.getDate() - 6); // últimos 7 dias
  } else if (periodo === "MENSAL") {
    fim = new Date(hoje);
    ini = new Date(hoje.getFullYear(), hoje.getMonth(), 1);
  } else if (periodo === "ANUAL") {
    fim = new Date(hoje);
    ini = new Date(hoje.getFullYear(), 0, 1);
  } else {
    return;
  }

  $("dataInicial").value = toISODate(ini);
  $("dataFinal").value = toISODate(fim);
}

function showLoading(show) {
  const loading = $("relatorioLoading");
  const result = $("resultadoRelatorio");

  if (!loading || !result) return;

  if (show) {
    loading.classList.remove("d-none");
    result.classList.add("d-none");
  } else {
    loading.classList.add("d-none");
    result.classList.remove("d-none");
  }
}

function setEmptyTableRows(tbodyId, cols = 4, text = "Sem dados") {
  const tbody = $(tbodyId);
  if (!tbody) return;
  tbody.innerHTML = `
    <tr>
      <td colspan="${cols}" class="text-muted">${text}</td>
    </tr>
  `;
}

function setEmptyList(listId, text = "Sem dados") {
  const el = $(listId);
  if (!el) return;
  el.innerHTML = `<li class="list-group-item text-muted">${text}</li>`;
}

function renderKPIs({ absenteismo, abertas, fechadas, total_gasto }) {
  $("kpiAbs").innerText = (absenteismo ?? 0) + "%";
  $("kpiAbertas").innerText = String(abertas ?? 0);
  $("kpiFechadas").innerText = String(fechadas ?? 0);
  $("kpiGasto").innerText = formatCurrencyBR(total_gasto);

  const f = Number(fechadas || 0);
  const gasto = Number(total_gasto || 0);
  const medio = f > 0 ? (gasto / f) : 0;

  $("kpiGastoInfo").innerText =
    `custo médio: ${formatCurrencyBR(medio)} / solicitação`;
}

function renderRankingUnidades(dados) {
  const tbody = $("tabelaUnidades");
  if (!tbody) return;

  if (!Array.isArray(dados) || !dados.length) {
    setEmptyTableRows("tabelaUnidades", 4);
    return;
  }

  let totalProvisionado = 0;
  let totalRealizado = 0;

  tbody.innerHTML = "";
  dados.forEach((u) => {
    const prov = Number(u.provisionado || 0);
    const real = Number(u.realizado || 0);
    totalProvisionado += prov;
    totalRealizado += real;

    tbody.innerHTML += `
      <tr>
        <td class="fw-semibold">${u.filial || "-"}</td>
        <td><span class="badge bg-primary">${Number(u.percentual || 0)}%</span></td>
        <td class="text-warning fw-bold">${formatCurrencyBR(prov)}</td>
        <td class="text-success fw-bold">${formatCurrencyBR(real)}</td>
      </tr>
    `;
  });

  $("financeProvisionado").innerText = formatCurrencyBR(totalProvisionado);
  $("financeRealizado").innerText = formatCurrencyBR(totalRealizado);
}

function renderRankingClientes(dados) {
  const list = $("listaClientes");
  if (!list) return;

  if (!Array.isArray(dados) || !dados.length) {
    setEmptyList("listaClientes");
    return;
  }

  list.innerHTML = "";
  dados.slice(0, 10).forEach((c) => {
    const nome = (c.cliente || "").trim() || "(sem cliente)";
    const perc = Number(c.percentual || 0);

    list.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        <span>${nome}</span>
        <span class="badge bg-warning">${perc}%</span>
      </li>
    `;
  });
}

function renderRankingTipos(dados) {
  const list = $("listaTipos");
  if (!list) return;

  if (!Array.isArray(dados) || !dados.length) {
    setEmptyList("listaTipos");
    return;
  }

  list.innerHTML = "";
  dados.slice(0, 10).forEach((t) => {
    const tipo = (t.tipo || "").trim() || "(sem tipo)";
    const perc = Number(t.percentual || 0);

    list.innerHTML += `
      <li class="list-group-item d-flex justify-content-between">
        <span>${tipo}</span>
        <span class="badge bg-info">${perc}%</span>
      </li>
    `;
  });
}

function renderFaltasPorData(dados) {
  faltasPorDataCache = Array.isArray(dados) ? dados : [];
  showingAllDates = false;

  const list = $("listaFaltasPorData");
  const btn = $("btnVerMaisDatas");

  if (!list) return;

  if (!faltasPorDataCache.length) {
    setEmptyList("listaFaltasPorData");
    if (btn) btn.classList.add("d-none");
    return;
  }

  const render = () => {
    list.innerHTML = "";

    const limite = showingAllDates ? faltasPorDataCache.length : 5;
    faltasPorDataCache.slice(0, limite).forEach((d) => {
      const dataISO = d.data;
      const dataFmt = formatDateBR(dataISO);
      const qtd = Number(d.qtd || 0);

      list.innerHTML += `
        <li class="list-group-item d-flex justify-content-between"
            style="cursor:pointer"
            data-iso="${dataISO}">
          <span>${dataFmt}</span>
          <span class="badge bg-danger">${qtd}</span>
        </li>
      `;
    });

    list.querySelectorAll("li[data-iso]").forEach((li) => {
      li.addEventListener("click", () => abrirModalFaltasPorData(li.dataset.iso));
    });

    if (btn) {
      if (faltasPorDataCache.length > 5) {
        btn.classList.remove("d-none");
        btn.innerText = showingAllDates ? "Recolher" : "Ver mais";
      } else {
        btn.classList.add("d-none");
      }
    }
  };

  render();

  if (btn) {
    btn.onclick = () => {
      showingAllDates = !showingAllDates;
      render();
    };
  }
}

function abrirModalFaltasPorData(dataISO) {
  const modalEl = $("modalFaltasData");
  if (!modalEl) return;

  const titulo = $("modalFaltasTitulo");
  const tbody = $("modalFaltasBody");
  const totalEl = $("modalFaltasTotal");

  const item = faltasPorDataCache.find((x) => x.data === dataISO);

  if (titulo) titulo.innerText = `Faltas — ${formatDateBR(dataISO)}`;
  if (tbody) tbody.innerHTML = "";
  if (totalEl) totalEl.innerText = "0";

  if (!item || !Array.isArray(item.funcionarios) || !item.funcionarios.length) {
    if (tbody) {
      tbody.innerHTML = `
        <tr>
          <td colspan="3" class="text-muted text-center">
            Nenhuma falta registrada
          </td>
        </tr>
      `;
    }
  } else {
    let total = 0;

    item.funcionarios.forEach((f) => {
      const matricula = f.matricula || "";
      const nome = f.nome || "";
      const qtd = Number(f.total || 0);
      total += qtd;

      tbody.innerHTML += `
        <tr>
          <td class="text-nowrap">${matricula}</td>
          <td>${nome}</td>
          <td class="text-end">
            <span class="badge bg-danger">${qtd}</span>
          </td>
        </tr>
      `;
    });

    if (totalEl) totalEl.innerText = String(total);
  }

  new bootstrap.Modal(modalEl).show();
}

async function gerarRelatorio() {
  const data_inicial = $("dataInicial")?.value || "";
  const data_final = $("dataFinal")?.value || "";
  const turno = $("turnoSelect")?.value || "";
  const filial = $("filialSelect")?.value || "";

  const params = new URLSearchParams({
    data_inicial,
    data_final,
    turno,
    filial
  });

  showLoading(true);

  try {
    const [
      respResumo,
      respSolicitacoes,
      respExtras,
      respClientes,
      respTipos,
      respAbsData
    ] = await Promise.all([
      fetch(`/api/dashboard/resumo?${params}`),
      fetch(`/api/dashboard/solicitacoes-resumo?${params}`),
      fetch(`/api/dashboard/extras?${params}`),
      fetch(`/api/dashboard/clientes?${params}`),
      fetch(`/api/dashboard/tipos-solicitacao?${params}`),
      fetch(`/api/dashboard/absenteismo-por-data?${params}`)
    ]);

    const dataResumo = await respResumo.json();
    const dataSolic = await respSolicitacoes.json();
    const dataExtras = await respExtras.json();
    const dataClientes = await respClientes.json();
    const dataTipos = await respTipos.json();
    const dataAbsData = await respAbsData.json();

    renderKPIs({
      absenteismo: dataResumo?.kpis?.absenteismo ?? 0,
      abertas: dataSolic?.abertas ?? 0,
      fechadas: dataSolic?.fechadas ?? 0,
      total_gasto: dataSolic?.total_gasto ?? 0
    });

    renderRankingUnidades(dataExtras);
    renderRankingClientes(dataClientes);
    renderRankingTipos(dataTipos);
    renderFaltasPorData(dataAbsData);

  } catch (e) {
    console.error("Erro ao gerar relatório:", e);

    setEmptyTableRows("tabelaUnidades", 4, "Erro ao carregar dados");
    setEmptyList("listaClientes", "Erro ao carregar dados");
    setEmptyList("listaTipos", "Erro ao carregar dados");
    setEmptyList("listaFaltasPorData", "Erro ao carregar dados");
  } finally {
    showLoading(false);
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const periodoSelect = $("periodoSelect");
  const form = $("formRelatorio");
  const btnLimpar = $("btnLimparFiltros");

  if (periodoSelect) {
    setPeriodoDefault(periodoSelect.value);

    periodoSelect.addEventListener("change", () => {
      const p = periodoSelect.value;
      if (p !== "CUSTOM") setPeriodoDefault(p);
    });
  }

  if (btnLimpar) {
    btnLimpar.addEventListener("click", () => {
      if (periodoSelect) periodoSelect.value = "MENSAL";
      if ($("turnoSelect")) $("turnoSelect").value = "";
      if ($("filialSelect")) $("filialSelect").value = "";
      setPeriodoDefault("MENSAL");
      gerarRelatorio();
    });
  }

  if (form) {
    form.addEventListener("submit", (e) => {
      e.preventDefault();
      gerarRelatorio();
    });
  }

  gerarRelatorio();
});
