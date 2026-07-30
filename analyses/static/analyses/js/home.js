// 找到分析表单和等待弹窗
const analysisForm = document.getElementById("analysis-form");
const analysePopup = document.getElementById("analyse-popup");

// 提交表单时显示弹窗
if (analysisForm) {
    analysisForm.addEventListener("submit", function (event) {
        // 暂停浏览器立即提交，让弹窗有时间显示
        event.preventDefault();

        analysePopup.hidden = false;

        // 弹窗显示后，再正常提交表单
        setTimeout(function () {
            analysisForm.submit();
        }, 100);
    });
}