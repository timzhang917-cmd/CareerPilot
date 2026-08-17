// 找到简历输入框和文件名显示区域
const resumeFileInput = document.getElementById("id_resume_file");
const resumeFileName = document.getElementById("resume-file-name");

// 用户选择简历后，显示真实文件名
if (resumeFileInput && resumeFileName) {
    resumeFileInput.addEventListener("change", function () {
        if (resumeFileInput.files.length > 0) {
            resumeFileName.textContent = resumeFileInput.files[0].name;
        } else {
            resumeFileName.textContent = "No file chosen";
        }
    });
}

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
