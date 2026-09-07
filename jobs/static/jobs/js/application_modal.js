// AI Usage Declaration:
// This file contains code generated with help of AI tools.
// Tool Used: ChatGPT
// Date Generated: 2026-08
// AI was used to assist with switching the application record modal between add and edit modes, 
// automatically populating form fields, reopening the modal after validation failure, and implementing deletion confirmation.
// The interaction flow was designed by the author.
// I have reviewed, tested, and understood the AI-generated code.

const applicationModal = document.getElementById("application-modal");
const openApplicationModalButton = document.getElementById(
    "open-application-modal"
);
const closeApplicationModalButtons = document.querySelectorAll(
    "[data-close-application-modal]"
);
const editApplicationButtons = document.querySelectorAll(
    "[data-edit-application]"
);
const applicationForm = applicationModal?.querySelector("form");
const applicationIdInput = document.getElementById("application-id");
const applicationModalTitle = document.getElementById(
    "application-modal-title"
);
const applicationModalSave = document.getElementById(
    "application-modal-save"
);

if (applicationModal && openApplicationModalButton) {
    openApplicationModalButton.addEventListener("click", () => {
        applicationForm.reset();
        applicationIdInput.value = "";
        applicationModalTitle.textContent = "Add Application";
        applicationModalSave.textContent = "Save Application";
        applicationModal.showModal();
    });

    editApplicationButtons.forEach((button) => {
        button.addEventListener("click", () => {
            applicationIdInput.value = button.dataset.applicationId; 
            applicationForm.elements.application_date.value =
                button.dataset.applicationDate;
            applicationForm.elements.company_name.value =
                button.dataset.companyName;
            applicationForm.elements.position_name.value =
                button.dataset.positionName;
            applicationForm.elements.location.value =
                button.dataset.location;
            applicationForm.elements.progress_notes.value =
                button.dataset.progressNotes;

            applicationModalTitle.textContent = "Edit Application";
            applicationModalSave.textContent = "Save Changes";
            applicationModal.showModal();
        });
    });

    closeApplicationModalButtons.forEach((button) => {
        button.addEventListener("click", () => {
            applicationModal.close();
        });
    });

    // if validation fails, automatically redisplay the error message after the page refreshes
    if (applicationModal.dataset.openAutomatically === "true") {
        applicationModal.showModal();
    }
}

// make sure that the user really wants to delete the application
const deleteApplicationForms = document.querySelectorAll(
    "[data-delete-application]"
);

deleteApplicationForms.forEach((form) => {
    form.addEventListener("submit", (event) => {
        const confirmed = window.confirm(
            "Are you sure?"
        );

        if (!confirmed) {
            event.preventDefault();
        }
    });
});
