
// CareCircle AI - Shared JavaScript

// 1. Language support
const translations = {
    en: {
        tagline: "Caring Together, Living Better.",
        userLabel: "Email Address",
        passwordLabel: "Password",
        remember: "Remember me",
        forgot: "Forgot password?",
        loginBtn: "Login",
        noAccount: "New here?",
        register: "Register"
    },

    gu: {
        tagline: "સાથે મળીને કાળજી, વધુ સારું જીવન.",
        userLabel: "ઇમેઇલ સરનામું",
        passwordLabel: "પાસવર્ડ",
        remember: "મને યાદ રાખો",
        forgot: "પાસવર્ડ ભૂલી ગયા?",
        loginBtn: "લૉગિન",
        noAccount: "નવા છો?",
        register: "નોંધણી કરો"
    },

    hi: {
        tagline: "साथ मिलकर देखभाल, बेहतर जीवन।",
        userLabel: "ईमेल पता",
        passwordLabel: "पासवर्ड",
        remember: "मुझे याद रखें",
        forgot: "पासवर्ड भूल गए?",
        loginBtn: "लॉगिन",
        noAccount: "नए हैं?",
        register: "रजिस्टर करें"
    }
};

const languageSelect = document.getElementById("languageSelect");

function setLanguage(lang) {
    if (!translations[lang]) {
        lang = "en";
    }

    document.querySelectorAll("[data-i18n]").forEach(function (element) {
        const key = element.dataset.i18n;

        if (translations[lang][key]) {
            element.textContent = translations[lang][key];
        }
    });

    document.documentElement.lang = lang;
    localStorage.setItem("language", lang);
    updateDateTime();
}

if (languageSelect) {
    const savedLanguage = localStorage.getItem("language") || "en";

    languageSelect.value = savedLanguage;
    setLanguage(savedLanguage);

    languageSelect.addEventListener("change", function () {
        setLanguage(languageSelect.value);
    });
}


// 2. Login page - Password Show/Hide

const togglePassword = document.getElementById("togglePassword");
const passwordInput = document.getElementById("password");

if (togglePassword && passwordInput) {
    togglePassword.addEventListener("click", function () {
        const isHidden = passwordInput.type === "password";

        passwordInput.type = isHidden ? "text" : "password";
        togglePassword.textContent = isHidden ? "Hide" : "Show";
    });
}


// 3. Forgot password message

const forgotLink = document.getElementById("forgotLink");

if (forgotLink) {
    forgotLink.addEventListener("click", function (event) {
        event.preventDefault();

        alert("Password reset functionality is not connected yet.");
    });
}


// 4. Dashboard date and time

function updateDateTime() {
    const dateTimeBox = document.getElementById("dateTime");

    if (!dateTimeBox) {
        return;
    }

    const lang = localStorage.getItem("language") || "en";

    const locales = {
        en: "en-IN",
        gu: "gu-IN",
        hi: "hi-IN"
    };

    dateTimeBox.textContent = new Date().toLocaleString(
        locales[lang],
        {
            dateStyle: "full",
            timeStyle: "short"
        }
    );
}

updateDateTime();
setInterval(updateDateTime, 30000);


// 5. AI Assistant - Integration pending

const chatForm = document.getElementById("chatForm");

if (chatForm) {
    chatForm.addEventListener("submit", function (event) {
        event.preventDefault();

        const input = document.getElementById("chatInput");
        const chatBox = document.getElementById("chatBox");

        const question = input.value.trim();

        if (!question) {
            return;
        }

        const userMessage = document.createElement("div");
        userMessage.className = "msg user";
        userMessage.textContent = question;

        chatBox.appendChild(userMessage);

        const botMessage = document.createElement("div");
        botMessage.className = "msg bot";
        botMessage.textContent =
            "AI Assistant integration is not connected yet. Please consult a healthcare professional for medical concerns.";

        chatBox.appendChild(botMessage);

        input.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;
    });
}

// 6. Save Health Readings

const healthForm = document.getElementById("healthForm");

if (healthForm) {
    healthForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        const heartRate = document.getElementById("heartRate").value;
        const systolic = document.getElementById("systolic").value;
        const diastolic = document.getElementById("diastolic").value;
        const steps = document.getElementById("steps").value;

        const message = document.getElementById("healthMessage");

        message.textContent = "Saving readings...";

        try {
            const response = await fetch("/save-health", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    heart_rate: heartRate,
                    systolic: systolic,
                    diastolic: diastolic,
                    steps: steps
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.message || "Unable to save readings.");
            }

            message.textContent = result.message;
            healthForm.reset();

        } catch (error) {
            message.textContent = error.message;
        }
    });
}
