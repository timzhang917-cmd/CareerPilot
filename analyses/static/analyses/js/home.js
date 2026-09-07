//AI Usage Declaration:
//-Line 35-47
//-This file contains code generated with help of AI tools.
//-Tool Used: ChatGPT
//-Date Generated: 2026-08
//-ChatGPT was used to solve the problem that
// the implemented loading pop-up did not appear when the form was submitted. 
// The suggested solution was to display the pop-up first and submit the form after a short delay.
//I have reviewed, tested, and understood the AI-generated code.



// find the resume file input and the span to display the file name
const resumeFileInput = document.getElementById("id_resume_file");
const resumeFileName = document.getElementById("resume-file-name");

// When the user selects a resume, display the real file name
if (resumeFileInput && resumeFileName) {
    resumeFileInput.addEventListener("change", function () {
        if (resumeFileInput.files.length > 0) {
            resumeFileName.textContent = resumeFileInput.files[0].name;
        } else {
            resumeFileName.textContent = "No file chosen";
        }
    });
}

// find the analysis form and the popup
const analysisForm = document.getElementById("analysis-form");
const analysePopup = document.getElementById("analyse-popup");

// Show the popup when the form is submitted
if (analysisForm) {
    analysisForm.addEventListener("submit", function (event) {
        // pause the browser's immediate submission to allow the popup to display
        event.preventDefault();

        analysePopup.hidden = false;

        // After the popup is displayed, submit the form normally
        setTimeout(function () {
            analysisForm.submit();
        }, 100);
    });
}
