// ─────────────────────────────────────────────
// Image Preview (Encode & Decode)
// ─────────────────────────────────────────────
function previewImage(input, previewId) {
    const preview = document.getElementById(previewId);
    if (!preview) return;

    if (input.files && input.files[0]) {
        const reader = new FileReader();

        reader.onload = function (e) {
            preview.src = e.target.result;
            preview.style.display = "block";
        };

        reader.readAsDataURL(input.files[0]);
    }
}

// ─────────────────────────────────────────────
// Form Validation
// ─────────────────────────────────────────────
function validateEncodeForm() {
    const imageInput = document.getElementById("image");
    const msgInput   = document.getElementById("message");
    const keyInput   = document.getElementById("key");

    if (!imageInput || imageInput.files.length === 0) {
        showToast("Please select an image.", false);
        return false;
    }
    if (!msgInput || msgInput.value.trim() === "") {
        showToast("Message cannot be empty.", false);
        return false;
    }
    if (!keyInput || keyInput.value.trim() === "") {
        showToast("Encryption key is required.", false);
        return false;
    }
    return true;
}

function validateDecodeForm() {
    const imageInput = document.getElementById("image");
    const keyInput   = document.getElementById("key");

    if (!imageInput || imageInput.files.length === 0) {
        showToast("Please select an image.", false);
        return false;
    }
    if (!keyInput || keyInput.value.trim() === "") {
        showToast("Decryption key is required.", false);
        return false;
    }
    return true;
}

// ─────────────────────────────────────────────
// Toast Notification
// ─────────────────────────────────────────────
function showToast(message, success = true) {
    // Remove existing toasts
    document.querySelectorAll(".toast-notification").forEach(t => t.remove());

    const toast = document.createElement("div");
    toast.className = "toast-notification";
    toast.innerText = message;

    Object.assign(toast.style, {
        position:     "fixed",
        bottom:       "24px",
        right:        "24px",
        padding:      "12px 20px",
        borderRadius: "10px",
        color:        "#fff",
        fontSize:     "14px",
        fontFamily:   "'DM Sans', sans-serif",
        fontWeight:   "500",
        zIndex:       "9999",
        background:   success ? "#22c55e" : "#ef4444",
        boxShadow:    "0 4px 16px rgba(0,0,0,0.15)",
        opacity:      "0",
        transform:    "translateY(8px)",
        transition:   "opacity 0.25s ease, transform 0.25s ease"
    });

    document.body.appendChild(toast);

    // Animate in
    requestAnimationFrame(() => {
        toast.style.opacity   = "1";
        toast.style.transform = "translateY(0)";
    });

    // Animate out and remove
    setTimeout(() => {
        toast.style.opacity   = "0";
        toast.style.transform = "translateY(8px)";
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// ─────────────────────────────────────────────
// Copy Decoded Message
// ─────────────────────────────────────────────
function copyMessage() {
    const textBox = document.getElementById("decodedMessage");
    if (!textBox) return;

    navigator.clipboard.writeText(textBox.value.trim())
        .then(() => showToast("Copied to clipboard!"))
        .catch(() => showToast("Copy failed.", false));
}

// ─────────────────────────────────────────────
// Auto-dismiss .alert elements
// ─────────────────────────────────────────────
window.addEventListener("DOMContentLoaded", function () {
    const alerts = document.querySelectorAll(".alert");

    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = "opacity 0.4s ease";
            alert.style.opacity    = "0";
            setTimeout(() => alert.remove(), 400);
        }, 4000);
    });
});

// ─────────────────────────────────────────────
// Password Toggle
// ─────────────────────────────────────────────
function togglePassword(id) {
    const input = document.getElementById(id);
    if (!input) return;

    input.type = input.type === "password" ? "text" : "password";
}

// ─────────────────────────────────────────────
// Loading Button State
// ─────────────────────────────────────────────
function setLoading(btn) {
    // Defer so form validation runs first
    setTimeout(() => {
        const form = btn.closest("form");
        // Only set loading if the form is valid (will submit)
        if (form && form.checkValidity()) {
            btn.disabled   = true;
            btn.innerText  = "Processing…";
            btn.style.opacity = "0.75";
        }
    }, 50);
}
