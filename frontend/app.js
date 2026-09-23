const API_URL = "http://localhost:8000";

let token = localStorage.getItem("vault_token");


/* =========================
   Navigation
========================= */

function hideAllPages() {
    document
        .querySelectorAll(".page, .auth-page")
        .forEach(page => {
            page.classList.add("hidden");
        });
}


function showPage(page) {

    if (!token) {
        showLogin();
        return;
    }

    hideAllPages();

    document
        .getElementById(page + "Page")
        .classList.remove("hidden");

    if (page === "dashboard") {
        loadCurrentUser();
    }
}


function showLogin() {

    hideAllPages();

    document
        .getElementById("loginPage")
        .classList.remove("hidden");
}


function showSignup() {

    hideAllPages();

    document
        .getElementById("signupPage")
        .classList.remove("hidden");
}


/* =========================
   Signup
========================= */

async function signup() {

    const name =
        document.getElementById("signupName").value;

    const email =
        document.getElementById("signupEmail").value;

    const password =
        document.getElementById("signupPassword").value;

    const organization_name =
        document.getElementById("signupOrganization").value;


    try {

        const response = await fetch(
            `${API_URL}/auth/signup`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    name,
                    email,
                    password,
                    organization_name
                })
            }
        );


        const data = await response.json();

        const message =
            document.getElementById("signupMessage");


        if (response.ok) {

            message.textContent =
                "Account created successfully. You can now login.";

            message.style.color = "green";

        } else {

            message.textContent =
                data.detail || "Signup failed.";

            message.style.color = "red";
        }

    } catch (error) {

        document.getElementById(
            "signupMessage"
        ).textContent =
            "Could not connect to Vault API.";

    }
}


/* =========================
   Login
========================= */

async function login() {

    const email =
        document.getElementById("loginEmail").value;

    const password =
        document.getElementById("loginPassword").value;


    try {

        const response = await fetch(
            `${API_URL}/auth/login`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    email,
                    password
                })
            }
        );


        const data = await response.json();


        const message =
            document.getElementById("loginMessage");


        if (response.ok) {

            token = data.access_token;

            localStorage.setItem(
                "vault_token",
                token
            );

            message.textContent =
                "Login successful.";

            message.style.color = "green";

            showPage("dashboard");

        } else {

            message.textContent =
                data.detail || "Login failed.";

            message.style.color = "red";
        }

    } catch (error) {

        document.getElementById(
            "loginMessage"
        ).textContent =
            "Could not connect to Vault API.";

    }
}


/* =========================
   Current User
========================= */

async function loadCurrentUser() {

    const response = await fetch(
        `${API_URL}/auth/users/me`,
        {
            headers: {
                "Authorization":
                    `Bearer ${token}`
            }
        }
    );


    if (response.status === 401) {

        logout();

        return;
    }


    const data = await response.json();


    document.getElementById(
        "userInfo"
    ).textContent =
        JSON.stringify(data, null, 2);
}


/* =========================
   Upload Document
========================= */

async function uploadDocument() {

    const fileInput =
        document.getElementById("documentFile");

    const message =
        document.getElementById("uploadMessage");


    if (!fileInput.files.length) {

        message.textContent =
            "Please select a PDF file.";

        message.style.color = "red";

        return;
    }


    const file = fileInput.files[0];


    if (!file.name.toLowerCase().endsWith(".pdf")) {

        message.textContent =
            "Only PDF files are allowed.";

        message.style.color = "red";

        return;
    }


    const formData = new FormData();

    formData.append(
        "file",
        file
    );


    try {

        const response = await fetch(
            `${API_URL}/documents/upload`,
            {
                method: "POST",

                headers: {
                    "Authorization":
                        `Bearer ${token}`
                },

                body: formData
            }
        );


        const data = await response.json();


        if (response.ok) {

            message.textContent =
                "Document uploaded successfully.";

            message.style.color = "green";


            document.getElementById(
                "documentId"
            ).value = data.document_id;


            document.getElementById(
                "documentResult"
            ).textContent =
                JSON.stringify(data, null, 2);

        } else {

            message.textContent =
                data.detail || "Upload failed.";

            message.style.color = "red";
        }

    } catch (error) {

        message.textContent =
            "Could not connect to Vault API.";

        message.style.color = "red";
    }
}


/* =========================
   Document Status
========================= */

async function getDocumentStatus() {

    const id =
        document.getElementById(
            "documentId"
        ).value;


    if (!id) {

        document.getElementById(
            "documentResult"
        ).textContent =
            "Enter a document ID.";

        return;
    }


    const response = await fetch(
        `${API_URL}/documents/${id}/status`,
        {
            headers: {
                "Authorization":
                    `Bearer ${token}`
            }
        }
    );


    const data = await response.json();


    document.getElementById(
        "documentResult"
    ).textContent =
        JSON.stringify(data, null, 2);
}


/* =========================
   Document Text
========================= */

async function getDocumentText() {

    const id =
        document.getElementById(
            "documentId"
        ).value;


    if (!id) {

        document.getElementById(
            "documentResult"
        ).textContent =
            "Enter a document ID.";

        return;
    }


    const response = await fetch(
        `${API_URL}/documents/${id}/text`,
        {
            headers: {
                "Authorization":
                    `Bearer ${token}`
            }
        }
    );


    const data = await response.json();


    document.getElementById(
        "documentResult"
    ).textContent =
        JSON.stringify(data, null, 2);
}


/* =========================
   Ask Vault / RAG
========================= */

async function askVault() {

    const query =
        document.getElementById("question").value;

    const answer =
        document.getElementById("answer");

    if (!query.trim()) {
        answer.textContent = "Please enter a question.";
        return;
    }

    answer.textContent = "Searching your documents...";

    try {

        const response = await fetch(
            `${API_URL}/documents/search`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json",
                    "Authorization": `Bearer ${token}`
                },

                body: JSON.stringify({
                    query: query
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            answer.textContent =
                data.detail || "Search failed.";
            return;
        }

        // Clear previous answer
        answer.innerHTML = "";

        // =========================
        // Answer
        // =========================

        const answerText = document.createElement("div");

        answerText.className = "answer-text";

        answerText.innerHTML = (data.answer || "No answer returned.")
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");

        answer.appendChild(answerText);


        // =========================
        // Sources
        // =========================

        if (data.sources && data.sources.length > 0) {

            const sourcesTitle = document.createElement("h4");

            sourcesTitle.textContent = "Sources";
            sourcesTitle.className = "sources-title";

            answer.appendChild(sourcesTitle);


            const sourcesContainer = document.createElement("div");

            sourcesContainer.className = "sources";


            // Remove duplicate chunks
            const uniqueSources = [];

            const seen = new Set();

            for (const source of data.sources) {

                const text = (source.text || "").trim();

                if (!text) {
                    continue;
                }

                // Normalize text for duplicate detection
                const normalized = text
                    .replace(/\s+/g, " ")
                    .toLowerCase();

                if (!seen.has(normalized)) {

                    seen.add(normalized);
                    uniqueSources.push(source);
                }

                // Maximum 3 sources
                if (uniqueSources.length === 3) {
                    break;
                }
            }


            uniqueSources.forEach((source, index) => {

                const sourceItem = document.createElement("div");

                sourceItem.className = "source-item";


                const title = document.createElement("strong");

                title.textContent = `Source ${index + 1}`;


                const snippet = document.createElement("p");

                let text = source.text;

                if (text.length > 180) {
                    text = text.substring(0, 180) + "...";
                }

                snippet.textContent = text;


                sourceItem.appendChild(title);
                sourceItem.appendChild(snippet);

                sourcesContainer.appendChild(sourceItem);
            });


            answer.appendChild(sourcesContainer);
        }

            } catch (error) {

                answer.textContent =
                    "Could not connect to Vault API.";
            }
}


/* =========================
   Logout
========================= */

function logout() {

    token = null;

    localStorage.removeItem(
        "vault_token"
    );

    showLogin();
}


/* =========================
   Initial Page
========================= */

if (token) {

    showPage("dashboard");

} else {

    showLogin();
}