document.addEventListener("DOMContentLoaded", function () {

  const selects = document.querySelectorAll(".select-acessar-fechadas");

  if (!selects.length) return;

  selects.forEach(select => {

    select.addEventListener("change", function () {

      const selected = this.value;
      if (!selected) return;

      const url = this.dataset[selected];

      if (url) {
        window.location.href = url;
      }

      this.value = "";
    });

  });

});
