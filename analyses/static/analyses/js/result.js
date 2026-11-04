// Show the submitted inputs in a side panel, next to the results they produced.
const inputDrawer = document.getElementById("input-drawer");

if (inputDrawer) {
    const openButtons = document.querySelectorAll("[data-input-open]");
    const tabs = inputDrawer.querySelectorAll("[data-input-tab]");
    const panels = inputDrawer.querySelectorAll("[data-input-panel]");
    let currentInput = null;

    function markCurrentInput() {
        openButtons.forEach(function (button) {
            button.classList.toggle("active", button.dataset.inputOpen === currentInput);
        });

        tabs.forEach(function (tab) {
            tab.classList.toggle("active", tab.dataset.inputTab === currentInput);
        });

        panels.forEach(function (panel) {
            panel.hidden = panel.dataset.inputPanel !== currentInput;
        });
    }

    function closeInputDrawer() {
        inputDrawer.close();
        currentInput = null;
        markCurrentInput();
    }

    openButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            // a second click on the same entry closes the panel
            if (currentInput === button.dataset.inputOpen) {
                closeInputDrawer();
                return;
            }

            currentInput = button.dataset.inputOpen;
            markCurrentInput();

            if (!inputDrawer.open) {
                inputDrawer.show();
            }
        });
    });

    // The panel can cover the entries above, so it has its own way to switch.
    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            currentInput = tab.dataset.inputTab;
            markCurrentInput();
        });
    });

    document.getElementById("input-drawer-close").addEventListener("click", closeInputDrawer);

    // Only a modal dialog closes on Escape by itself.
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && inputDrawer.open) {
            closeInputDrawer();
        }
    });
}
