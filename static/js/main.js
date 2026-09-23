// Переключение карточек резидентов
document.querySelectorAll("[data-resident]").forEach((tab) => {
  tab.addEventListener("click", () => {
    const id = tab.dataset.resident;

    document.querySelectorAll("[data-resident]").forEach((t) => {
      const active = t === tab;
      t.classList.toggle("is-active", active);
      t.setAttribute("aria-selected", active ? "true" : "false");
    });

    document.querySelectorAll(".resident-panel").forEach((panel) => {
      panel.hidden = panel.id !== "panel-" + id;
    });
  });
});

// «Отправить ещё одну заявку» — показать форму снова
const resetLink = document.querySelector("[data-reset-form]");
if (resetLink) {
  resetLink.addEventListener("click", (event) => {
    event.preventDefault();
    resetLink.closest(".success").hidden = true;
    const form = document.querySelector("#apply form");
    form.hidden = false;
    form.reset();
    form.querySelector("input[name=full_name]").focus();
  });
}
