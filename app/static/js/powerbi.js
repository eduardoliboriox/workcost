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
