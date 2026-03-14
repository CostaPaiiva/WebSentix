document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".tab-btn");
    const panels = document.querySelectorAll(".mode-panel");
    const inputType = document.getElementById("input_type");
    const form = document.getElementById("analysis-form");
    const loading = document.getElementById("loading-indicator");

    buttons.forEach((button) => {
        button.addEventListener("click", () => {
            const mode = button.dataset.mode;

            buttons.forEach((btn) => btn.classList.remove("active"));
            button.classList.add("active");

            panels.forEach((panel) => panel.classList.remove("active"));
            const activePanel = document.getElementById(`panel-${mode}`);
            if (activePanel) {
                activePanel.classList.add("active");
            }

            if (inputType) {
                inputType.value = mode;
            }
        });
    });

    if (form) {
        form.addEventListener("submit", () => {
            if (loading) {
                loading.classList.remove("hidden");
            }
        });
    }
});
