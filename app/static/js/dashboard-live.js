async function atualizarDashboard() {
  try {
    const params = new URLSearchParams({
      data_inicial: document.querySelector('[name="data_inicial"]').value,
      data_final: document.querySelector('[name="data_final"]').value,
      turno: document.querySelector('[name="turno"]').value || '',
      filial: document.querySelector('[name="filial"]').value || ''
    });

    const resp = await fetch(`/api/dashboard/resumo?${params}`);
    const data = await resp.json();

    // ===== KPIs =====
    document.getElementById("kpi-hc-planejado").innerText = data.kpis.hc_planejado;
    document.getElementById("kpi-hc-real").innerText = data.kpis.hc_real;
    document.getElementById("kpi-ausencias").innerText = data.kpis.ausencias;
    document.getElementById("kpi-abs").innerText = data.kpis.absenteismo + "%";
    document.getElementById("kpi-linhas").innerText = data.kpis.linhas;

    // (Opcional depois) atualizar rankings sem reload

  } catch (e) {
    console.error("Erro ao atualizar dashboard", e);
  }
}

// polling igual Power BI
setInterval(atualizarDashboard, 5000);
document.addEventListener("DOMContentLoaded", atualizarDashboard);


<script>
document.addEventListener("DOMContentLoaded", function () {

  const form = document.getElementById("dashboardFilters");
  if (!form) return;

  form.querySelectorAll("input, select").forEach(el => {
    el.addEventListener("change", () => form.submit());
  });

});
</script>
