
document.addEventListener("DOMContentLoaded", function () {

    // =====================================
    // 1. DOMAIN KNOWLEDGE (Q3)
    // =====================================

    const domainOptions = document.querySelectorAll(
        'input[name="knowDomain"]'
    );

    const explanationBox = document.getElementById("explanationBox");
    const unknownDomains = document.getElementById("unknownDomains");

    domainOptions.forEach(option => {
        option.addEventListener("change", function () {

            if (this.value === "Yes") {
                explanationBox?.classList.remove("hidden");
                unknownDomains?.classList.add("hidden");
            } else {
                explanationBox?.classList.add("hidden");
                unknownDomains?.classList.remove("hidden");
            }

        });
    });


    // =====================================
    // 2. DOMAIN TYPES (Q4)
    // =====================================

    const domainTypeOptions = document.querySelectorAll(
        'input[name="knowTypes"]'
    );

    const knownDomains = document.getElementById("knownDomains");

    domainTypeOptions.forEach(option => {
        option.addEventListener("change", function () {

            if (this.value === "Yes") {
                knownDomains?.classList.remove("hidden");
            } else {
                knownDomains?.classList.add("hidden");
            }

        });
    });


    // =====================================
    // 3. INTRODUCTION VIDEO (Q5)
    // =====================================

    const watchVideo = document.getElementById("watchVideo");
    const videoModal = document.getElementById("videoModal");
    const closeVideo = document.getElementById("closeVideo");
    const domainVideo = document.getElementById("domainVideo");
    const videoAnswerBox = document.getElementById("videoAnswerBox");

    watchVideo?.addEventListener("click", function () {

        if (videoModal) {
            videoModal.style.display = "flex";
        }

        if (domainVideo) {
            domainVideo.src =
                "https://www.youtube.com/embed/ukzFI9rgwfU?autoplay=1";
        }

    });

    closeVideo?.addEventListener("click", function () {

        if (videoModal) {
            videoModal.style.display = "none";
        }

        if (domainVideo) {
            domainVideo.src = "";
        }

        videoAnswerBox?.classList.remove("hidden");

    });


    // =====================================
    // 4. STUDENT ASSESSMENT API
    // =====================================

    const studentForm = document.getElementById("studentForm");

    studentForm?.addEventListener("submit", async function (event) {

        event.preventDefault();

        const studentData = {

            name: document.getElementById("Q1")?.value.trim() || "",

            college: document.querySelector(
                'input[name="college"]:checked'
            )?.value || "",

            knowDomain: document.querySelector(
                'input[name="knowDomain"]:checked'
            )?.value || "",

            domainExplanation:
                document.getElementById("domainExplanation")?.value || "",

            knowTypes: document.querySelector(
                'input[name="knowTypes"]:checked'
            )?.value || "",

            knownDomains: Array.from(
                document.querySelectorAll(
                    'input[name="domains"]:checked'
                )
            ).map(item => item.value),

            videoAnswer:
                document.getElementById("videoAnswer")?.value || "",

            preferredDomain:
                document.getElementById("preferredDomain")?.value || ""

        };


        // Validation

        if (!studentData.name) {
            alert("Please enter your name.");
            return;
        }

        if (!studentData.college) {
            alert("Please select your college category.");
            return;
        }

        if (!studentData.knowDomain) {
            alert("Please answer Question 3.");
            return;
        }

        if (!studentData.knowTypes) {
            alert("Please answer Question 4.");
            return;
        }

        if (!studentData.preferredDomain) {
            alert("Please select your preferred domain.");
            return;
        }


        // Submit to Flask API

        const submitButton = studentForm.querySelector(
            'button[type="submit"]'
        );

        try {

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.textContent = "Saving Assessment...";
            }

            const response = await fetch(
                "https://skillbridge-ai-lep0.onrender.com/api/assessment",
                {
                    method: "POST",

                    credentials: "include",

                    headers: {
                        "Content-Type": "application/json"
                    },

                    body: JSON.stringify(studentData)
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(
                    result.error || "Assessment submission failed."
                );
            }

            // Save temporary frontend copy

            sessionStorage.setItem(
                "studentData",
                JSON.stringify(studentData)
            );

            alert("Assessment saved successfully!");

            window.location.href = "dashboard.html";

        } catch (error) {

            console.error("Assessment Error:", error);

            alert(error.message || "Backend connection failed.");

        } finally {

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.textContent = "Submit Assessment";
            }

        }

    });


    // =====================================
    // 5. LOGIN PAGE PASSWORD TOGGLE
    // =====================================

    const password = document.getElementById("pass");
    const togglePassword = document.getElementById("togglePassword");

    togglePassword?.addEventListener("click", function () {

        if (password.type === "password") {
            password.type = "text";
            this.textContent = "Hide";
        } else {
            password.type = "password";
            this.textContent = "Show";
        }

    });


    // =====================================
    // 6. LOGIN API
    // =====================================

    const loginForm = document.getElementById("loginForm");

    loginForm?.addEventListener("submit", async function (event) {

        event.preventDefault();

        const email = document.getElementById("email").value.trim();
        const pass = document.getElementById("pass").value;

        if (!email || !pass) {
            alert("Please enter email and password.");
            return;
        }

        try {

            const response = await fetch(
                "https://skillbridge-ai-lep0.onrender.com/api/login",
                {
                    method: "POST",
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        email: email,
                        password: pass
                    })
                }
            );

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Login failed.");
            }

            sessionStorage.setItem(
                "loggedIn",
                "true"
            );

            sessionStorage.setItem(
                "loginEmail",
                result.student.email
            );

            sessionStorage.setItem(
                "studentData",
                JSON.stringify({
                    name: result.student.name,
                    email: result.student.email
                })
            );

            alert("Login successful!");

            window.location.href = "form.html";

        } catch (error) {

            console.error("Login Error:", error);
            alert(error.message);

        }

    });


    // =====================================
    // 7. CANCEL BUTTON
    // =====================================

    document.getElementById("cancelBtn")?.addEventListener(
        "click",
        function () {

            loginForm?.reset();

            if (password) {
                password.type = "password";
            }

            if (togglePassword) {
                togglePassword.textContent = "Show";
            }

        }
    );


    // =====================================
    // 8. GOOGLE LOGIN DEMO
    // =====================================

    document.getElementById("googleLogin")?.addEventListener(
        "click",
        function () {
            alert(
                "Google login requires Google OAuth configuration."
            );
        }
    );


    // =====================================
    // 9. FORGOT PASSWORD
    // =====================================

    document.getElementById("forgotPassword")?.addEventListener(
        "click",
        function (event) {

            event.preventDefault();

            alert(
                "Please contact the project administrator for password reset."
            );

        }
    );

});
