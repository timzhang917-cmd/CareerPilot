document.addEventListener("DOMContentLoaded", function () {
    const openButton = document.getElementById("profile-open");
    const modal = document.getElementById("profile-modal");
    const closeX = document.getElementById("profile-close-x");
    const closeButton = document.getElementById("profile-close-button");


    if (!openButton || !modal) {
        return;
    }

    function openProfile() {
        modal.hidden = false;
        document.body.classList.add("profile-modal-open");
    }

    function closeProfile() {
        modal.hidden = true;
        document.body.classList.remove("profile-modal-open");
        openButton.focus();
    }

    openButton.addEventListener("click", openProfile);
    closeX.addEventListener("click", closeProfile);
    closeButton.addEventListener("click", closeProfile);

    // close when clicking outside the modal
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeProfile();
        }
    });

    // close when pressing the Esc key
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.hidden) {
            closeProfile();
        }
    });
});
