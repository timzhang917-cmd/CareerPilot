document.addEventListener("DOMContentLoaded", () => {
    const modal = document.getElementById("job-post-modal");
    const openButton = document.getElementById("open-job-post-modal");

    if (!modal || !openButton) {
        return;
    }

    const closeButtons = modal.querySelectorAll(
        "[data-close-job-post-modal]"
    );

    openButton.addEventListener("click", () => {
        modal.showModal();
    });

    closeButtons.forEach((button) => {
        button.addEventListener("click", () => {
            modal.close();
        });
    });

    // 服务端校验失败后，自动重新打开弹窗显示错误。
    if (modal.dataset.openAutomatically === "true") {
        modal.showModal();
    }
});
