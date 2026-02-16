async function atualizarDashboard() {
  try {
    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value || '',
      filial: document.querySelector('[name="filial"]').value || ''
    });

    // ===============================
    // KPIs
    // ===============================
    const respResumo = await fetch(`/api/dashboard/resumo?${params}`);
    const dataResumo = await respResumo.json();

    document.getElementById("kpi-hc-planejado").innerText = dataResumo.kpis.hc_planejado;
    document.getElementById("kpi-hc-real").innerText = dataResumo.kpis.hc_real;
    document.getElementById("kpi-ausencias").innerText = dataResumo.kpis.ausencias;
    document.getElementById("kpi-abs").innerText = dataResumo.kpis.absenteismo + "%";
    document.getElementById("kpi-linhas").innerText = dataResumo.kpis.linhas;

    // ===============================
    // Ranking Extras (NOVO)
    // ===============================
    const respExtras = await fetch(`/api/dashboard/extras?${params}`);
    const rankingExtras = await respExtras.json();

    atualizarTabelaExtras(rankingExtras);

  } catch (e) {
    console.error("Erro ao atualizar dashboard", e);
  }
}

function atualizarTabelaExtras(dados) {

  const tbody = document.querySelector("#rankingExtrasBody");
  if (!tbody) return;

  tbody.innerHTML = "";

  dados.forEach(f => {
    tbody.innerHTML += `
      <tr>
        <td class="fw-semibold">${f.filial}</td>
        <td>
          <span class="badge bg-primary">
            ${f.percentual}%
          </span>
        </td>
        <td class="text-warning fw-bold">
          R$ ${f.provisionado.toFixed(2)}
        </td>
        <td class="text-success fw-bold">
          R$ ${f.realizado.toFixed(2)}
        </td>
      </tr>
    `;
  });
}

// ===============================
// Filtros -> atualizar sem reload
// ===============================
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

// polling
setInterval(atualizarDashboard, 5000);
