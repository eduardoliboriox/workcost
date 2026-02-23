function safeNumber(value) {
  const n = Number(value);
  return Number.isFinite(n) ? n : 0;
}

function formatSignedNumber(n) {
  const num = safeNumber(n);
  if (num > 0) return `+${num}`;
  return `${num}`;
}

function clampPercent(p) {
  const n = safeNumber(p);
  if (n < 0) return 0;
  if (n > 100) return 100;
  return n;
}

function buildExecutiveSummary({
  hcPlanejado,
  hcReal,
  gap,
  ausencias,
  absPercent,
  linhasCriticas,
  totalLinhasRanking,
  totalFaltasRanking
}) {
  const statusHc =
    gap < 0 ? "abaixo" : (gap > 0 ? "acima" : "em linha");

  const statusCritico =
    linhasCriticas > 0
      ? "atenção imediata"
      : "operação estável";

  return `
    No período filtrado, o HC real está <strong>${statusHc}</strong> do planejado
    (<strong>${hcReal}</strong> vs <strong>${hcPlanejado}</strong>, GAP <strong>${formatSignedNumber(gap)}</strong>).
    Foram registradas <strong>${ausencias}</strong> ausências, com absenteísmo geral em <strong>${absPercent}%</strong>.
    No ranking atual, <strong>${linhasCriticas}</strong> de <strong>${totalLinhasRanking}</strong> linhas estão em condição crítica
    (total de <strong>${totalFaltasRanking}</strong> faltas somadas no ranking).
    Direcionamento: <strong>${statusCritico}</strong>.
  `.trim();
}

function renderTopLinhas(ranking) {
  const ul = document.getElementById("topLinhasList");
  if (!ul) return;

  ul.innerHTML = "";

  const top = (Array.isArray(ranking) ? ranking : [])
    .slice()
    .sort((a, b) => safeNumber(b.faltas) - safeNumber(a.faltas))
    .slice(0, 5);

  if (!top.length) {
    ul.innerHTML = `
      <li class="list-group-item text-muted">
        Sem dados para exibir com os filtros atuais.
      </li>
    `;
    return;
  }

  top.forEach((l, idx) => {
    const linha = l.linha || "-";
    const faltas = safeNumber(l.faltas);
    const isCritico = (l.status || "").toUpperCase() === "CRITICO";

    ul.innerHTML += `
      <li class="list-group-item d-flex justify-content-between align-items-center"
          style="cursor:pointer"
          onclick="abrirModalLinhaPowerBI('${linha}')">
        <div class="d-flex align-items-center gap-2">
          <span class="badge ${isCritico ? "bg-danger" : "bg-success"}">${idx + 1}</span>
          <span class="fw-semibold">${linha}</span>
        </div>
        <span class="badge bg-dark">${faltas}</span>
      </li>
    `;
  });
}

function renderExecutiveWidgets(data) {
  const kpis = data?.kpis || {};
  const ranking = Array.isArray(data?.ranking_faltas) ? data.ranking_faltas : [];

  const hcPlanejado = safeNumber(kpis.hc_planejado);
  const hcReal = safeNumber(kpis.hc_real);
  const ausencias = safeNumber(kpis.ausencias);
  const absPercent = safeNumber(kpis.absenteismo);

  const gap = hcReal - hcPlanejado;

  const linhasCriticas = ranking.filter(
    x => (x.status || "").toUpperCase() === "CRITICO"
  ).length;

  const totalFaltasRanking = ranking.reduce(
    (acc, x) => acc + safeNumber(x.faltas),
    0
  );

  const totalLinhasRanking = ranking.length;

  // KPI GAP HC
  const gapEl = document.getElementById("kpi-gap-hc");
  if (gapEl) {
    gapEl.innerText = formatSignedNumber(gap);
    gapEl.classList.remove("text-muted", "text-success", "text-danger");
    if (gap < 0) gapEl.classList.add("text-danger");
    else if (gap > 0) gapEl.classList.add("text-success");
    else gapEl.classList.add("text-muted");
  }

  // chips executivos
  const critEl = document.getElementById("kpi-linhas-criticas");
  if (critEl) critEl.innerText = String(linhasCriticas);

  const totalEl = document.getElementById("kpi-total-faltas");
  if (totalEl) totalEl.innerText = String(totalFaltasRanking);

  // resumo texto
  const summaryEl = document.getElementById("exec-summary-text");
  if (summaryEl) {
    summaryEl.innerHTML = buildExecutiveSummary({
      hcPlanejado,
      hcReal,
      gap,
      ausencias,
      absPercent,
      linhasCriticas,
      totalLinhasRanking,
      totalFaltasRanking
    });
  }

  // barra HC (real / planejado)
  const barHc = document.getElementById("bar-hc-real");
  const barHcLabel = document.getElementById("bar-hc-label");

  if (barHc) {
    const denom = hcPlanejado > 0 ? hcPlanejado : (hcReal > 0 ? hcReal : 1);
    const pct = clampPercent((hcReal / denom) * 100);

    barHc.style.width = `${pct}%`;

    // cor pela condição (sem mexer em css global)
    barHc.classList.remove("bg-success", "bg-danger", "bg-warning");
    if (gap < 0) barHc.classList.add("bg-danger");
    else if (gap > 0) barHc.classList.add("bg-warning");
    else barHc.classList.add("bg-success");
  }

  if (barHcLabel) {
    barHcLabel.innerText = `${hcReal} / ${hcPlanejado}`;
  }

  // barra de status (% crítico)
  const barCrit = document.getElementById("bar-status-critico");
  const barStatusLabel = document.getElementById("bar-status-label");

  if (barCrit) {
    const pctCrit = totalLinhasRanking > 0
      ? clampPercent((linhasCriticas / totalLinhasRanking) * 100)
      : 0;

    barCrit.style.width = `${pctCrit}%`;
    if (barStatusLabel) barStatusLabel.innerText = `${pctCrit.toFixed(0)}% crítico`;
  }

  // top linhas
  renderTopLinhas(ranking);
}

async function atualizarPowerBI() {
  try {
    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value,
      filial: document.querySelector('[name="filial"]').value,
      setor: document.querySelector('[name="setor"]').value,
      linha: document.querySelector('[name="linha"]').value
    });

    const resp = await fetch(`/api/powerbi/resumo?${params}`);
    const data = await resp.json();

    // ===== KPIs =====
    document.querySelector("#kpi-hc-planejado").innerText = data.kpis.hc_planejado;
    document.querySelector("#kpi-hc-real").innerText = data.kpis.hc_real;
    document.querySelector("#kpi-ausencias").innerText = data.kpis.ausencias;
    document.querySelector("#kpi-abs").innerText = data.kpis.absenteismo + "%";
    document.querySelector("#kpi-linhas").innerText = data.kpis.linhas;

    // ===== EXECUTIVE WIDGETS (NOVO) =====
    renderExecutiveWidgets(data);

    // ===== RANKING DE LINHAS =====
    const container = document.querySelector("#rankingPowerBI");
    container.innerHTML = "";

    const max = Math.max(...data.ranking_faltas.map(l => l.altura), 1);

    data.ranking_faltas.forEach(l => {
      container.innerHTML += `
        <div class="text-center" style="width:60px; cursor:pointer"
             onclick="abrirModalLinhaPowerBI('${l.linha}')">
          <div class="fw-bold small">${l.faltas}</div>
          <div style="
            height:${(l.altura * 180) / max}px;
            background:${l.status === 'CRITICO' ? '#dc3545' : '#198754'};
            border-radius:6px;">
          </div>
          <small>${l.linha}</small>
        </div>
      `;
    });

  } catch (e) {
    console.error("Erro ao atualizar PowerBI", e);
  }
}

// Polling inteligente
setInterval(atualizarPowerBI, 5000);
document.addEventListener("DOMContentLoaded", atualizarPowerBI);
