
// Q3: Domain Knowledge

const domainOptions = document.querySelectorAll(
    'input[name="knowDomain"]'
);

const explanationBox = document.getElementById("explanationBox");
const unknownDomains = document.getElementById("unknownDomains");

domainOptions.forEach(function(option) {

    option.addEventListener("change", function() {

        if (this.value === "Yes") {

            explanationBox.classList.remove("hidden");
            unknownDomains.classList.add("hidden");

        } else {

            explanationBox.classList.add("hidden");
            unknownDomains.classList.remove("hidden");

        }

    });

});

// Q4: Different Types of Domains

const domainTypeOptions = document.querySelectorAll(
    'input[name="knowTypes"]'
);

const knownDomains = document.getElementById("knownDomains");

domainTypeOptions.forEach(function(option) {

    option.addEventListener("change", function() {

        if (this.value === "Yes") {

            knownDomains.classList.remove("hidden");

        } else {

            knownDomains.classList.add("hidden");

        }

    });

});

// Q5: Introduction Video Popup

const watchVideo = document.getElementById("watchVideo");
const videoModal = document.getElementById("videoModal");
const closeVideo = document.getElementById("closeVideo");
const domainVideo = document.getElementById("domainVideo");
const videoAnswerBox = document.getElementById("videoAnswerBox");

// Open video popup

watchVideo.addEventListener("click", function() {

    videoModal.style.display = "flex";

    domainVideo.src =
    "https://www.youtube.com/embed/ukzFI9rgwfU";

});

// Close video popup

closeVideo.addEventListener("click", function() {

    videoModal.style.display = "none";

    domainVideo.src = "";

    videoAnswerBox.classList.remove("hidden");

});

// Step 5: Assessment Form Submission



const studentForm = document.getElementById("studentForm");

studentForm.addEventListener("submit", function(event) {

    event.preventDefault();

    const studentData = {

        name: document.getElementById("Q1").value.trim(),

        college: document.querySelector(
            'input[name="college"]:checked'
        )?.value || "",

        knowDomain: document.querySelector(
            'input[name="knowDomain"]:checked'
        )?.value || "",

        domainExplanation:
            document.getElementById("domainExplanation").value,

        knowTypes: document.querySelector(
            'input[name="knowTypes"]:checked'
        )?.value || "",

        knownDomains: Array.from(
            document.querySelectorAll('input[name="domains"]:checked')
        ).map(item => item.value),

        videoAnswer:
            document.getElementById("videoAnswer").value,

        preferredDomain:
            document.getElementById("preferredDomain").value

    };

    if (studentData.name === "") {
        alert("Please enter your name.");
        return;
    }

    if (studentData.preferredDomain === "") {
        alert("Please select your preferred domain.");
        return;
    }

    // Save assessment data temporarily
    sessionStorage.setItem(
        "studentData",
        JSON.stringify(studentData)
    );

    alert("Assessment submitted successfully!");

    window.location.href = "dashboard.html";

});

if (studentData) {

    document.getElementById("studentName").textContent =
        studentData.name || "Student";

    document.getElementById("studentDomain").textContent =
        studentData.preferredDomain || "Not Selected";

    document.getElementById("collegeType").textContent =
        studentData.college || "Not Available";

} else {

    document.getElementById("studentName").textContent =
        "Student";

}

// Step 9: Industry Required Skills

const skillsData = {

    "AI / Machine Learning": [
        "Python",
        "NumPy",
        "Pandas",
        "Statistics",
        "Machine Learning",
        "Scikit-learn",
        "Deep Learning",
        "Natural Language Processing",
        "Model Deployment"
    ],

    "Data Science": [
        "Python",
        "Statistics",
        "SQL",
        "Pandas",
        "Data Visualization",
        "Machine Learning"
    ],

    "Web Development": [
        "HTML",
        "CSS",
        "JavaScript",
        "Python",
        "Flask",
        "SQL",
        "API Development"
    ],

    "Cybersecurity": [
        "Networking",
        "Linux",
        "Python",
        "Web Security",
        "Cryptography",
        "Ethical Hacking"
    ],

    "Cloud Computing": [
        "Linux",
        "Networking",
        "AWS",
        "Cloud Architecture",
        "Docker",
        "Security"
    ]

};

const skillsContent = document.getElementById("skillsContent");

if (studentData && studentData.preferredDomain) {

    const selectedDomain = studentData.preferredDomain;

    const skills = skillsData[selectedDomain] || [
        "Programming Fundamentals",
        "Domain Fundamentals",
        "Problem Solving",
        "Industry Tools",
        "Practical Projects"
    ];

    skillsContent.innerHTML = "";

    skills.forEach(function(skill) {

        const skillItem = document.createElement("p");

        skillItem.textContent = "✓ " + skill;

        skillsContent.appendChild(skillItem);

    });

} else {

    skillsContent.textContent =
        "Please complete your student assessment first.";

}
