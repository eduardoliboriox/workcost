document.addEventListener("DOMContentLoaded", () => {

  document.querySelectorAll("select[data-pdf]").forEach(select => {

    select.addEventListener("change", function () {

      const selected = this.value;

      if (!selected) return;

      if (selected === "pdf") {
        window.location.href = this.dataset.pdf;
      }

      if (selected === "frequencia") {
        alert("Tela de frequência será implementada no próximo passo.");
      }

      this.value = "";
    });

  });

});
