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
        // 新增时清空可能残留的编辑内容
        applicationForm.reset();
        applicationIdInput.value = "";
        applicationModalTitle.textContent = "Add Application";
        applicationModalSave.textContent = "Save Application";
        applicationModal.showModal();
    });

    editApplicationButtons.forEach((button) => {
        button.addEventListener("click", () => {
            // 把刚才保存的数据写入弹窗中
            applicationIdInput.value = button.dataset.applicationId; //把当前记录写入了隐藏输入框
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

    // 如果表单校验失败，页面刷新后自动重新展示错误信息
    if (applicationModal.dataset.openAutomatically === "true") {
        applicationModal.showModal();
    }
}

// 删除前二次确认，避免用户误删投递记录
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
