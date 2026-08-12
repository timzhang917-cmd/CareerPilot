document.addEventListener("DOMContentLoaded", function () {
    const openButton = document.getElementById("profile-open");
    const modal = document.getElementById("profile-modal");
    const closeX = document.getElementById("profile-close-x");
    const closeButton = document.getElementById("profile-close-button");

    // 未登录时页面不存在这些元素，因此停止执行
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

    // 点击弹窗外面的灰色遮罩时关闭
    modal.addEventListener("click", function (event) {
        if (event.target === modal) {
            closeProfile();
        }
    });

    // 按下 Esc 键时关闭
    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && !modal.hidden) {
            closeProfile();
        }
    });
});
