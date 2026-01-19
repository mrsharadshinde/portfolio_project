/**
 * script.js - Portfolio Interactive Logic
 * Optimized for Slider and View More/Less functionality
 */

document.addEventListener('DOMContentLoaded', () => {
    console.log("DOM Fully Loaded and Parsed");

    // --- 1. Theme Toggle Logic ---
    const themeToggleBtn = document.getElementById("theme-toggle");
    const darkIcon = document.getElementById("theme-toggle-dark-icon");
    const lightIcon = document.getElementById("theme-toggle-light-icon");

    function updateThemeIcons() {
        if (document.documentElement.classList.contains("dark")) {
            lightIcon?.classList.remove("hidden");
            darkIcon?.classList.add("hidden");
        } else {
            darkIcon?.classList.remove("hidden");
            lightIcon?.classList.add("hidden");
        }
    }
    updateThemeIcons();

    themeToggleBtn?.addEventListener("click", function () {
        document.documentElement.classList.toggle("dark");
        const isDark = document.documentElement.classList.contains("dark");
        localStorage.setItem("color-theme", isDark ? "dark" : "light");
        updateThemeIcons();
    });

    // --- 2. Active Section Navbar Tracker ---
    window.addEventListener('scroll', () => {
        let current = '';
        const sections = document.querySelectorAll('section');
        const navLinks = document.querySelectorAll('.nav-link');
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            if (pageYOffset >= sectionTop - 150) {
                current = section.getAttribute('id');
            }
        });
        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href').includes(current)) {
                link.classList.add('active');
            }
        });
    });

    // --- 3. Certificate Slider Logic ---
    const certSlider = document.querySelector('#cert-slider');
    const nextCertBtn = document.querySelector('#next-cert');
    const prevCertBtn = document.querySelector('#prev-cert');

    if (certSlider && nextCertBtn && prevCertBtn) {
        nextCertBtn.onclick = () => certSlider.scrollBy({ left: 400, behavior: 'smooth' });
        prevCertBtn.onclick = () => certSlider.scrollBy({ left: -400, behavior: 'smooth' });
    }

   

    // --- 5. AJAX Contact Form Logic ---
    const contactForm = document.getElementById("contact-form");
    contactForm?.addEventListener("submit", function (e) {
        e.preventDefault();
        const submitBtn = this.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerText;
        submitBtn.innerText = "Sending...";
        submitBtn.disabled = true;

        Swal.fire({
            title: "Sending...",
            text: "Please wait.",
            allowOutsideClick: false,
            didOpen: () => Swal.showLoading(),
        });

        const formData = new FormData(this);
        fetch(window.location.href, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value,
            },
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === "success") {
                Swal.fire({ title: "Sent!", text: data.message, icon: "success", confirmButtonColor: "#1B325F" });
                contactForm.reset();
            }
        })
        .catch(() => Swal.fire({ title: "Error!", text: "Unable to send.", icon: "error" }))
        .finally(() => {
            submitBtn.innerText = originalText;
            submitBtn.disabled = false;
        });
    });

    // --- 6. Chatbot Streaming Logic ---
    const chatForm = document.getElementById("ai-chat-form");
    chatForm?.addEventListener("submit", function (e) {
        e.preventDefault();
        const input = document.getElementById("ai-user-input");
        const msgContainer = document.getElementById("chat-messages");
        const query = input.value;

        msgContainer.innerHTML += `
            <div class="flex justify-end mb-4">
                <div class="bg-navy text-white p-4 rounded-2xl rounded-tr-none shadow-md max-w-[80%] text-sm">
                    ${query}
                </div>
            </div>`;
        input.value = "";
        msgContainer.scrollTop = msgContainer.scrollHeight;

        const loaderId = "loader-" + Date.now();
        msgContainer.innerHTML += `
            <div id="${loaderId}" class="flex justify-start mb-4">
                <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-sky/5 dark:border-slate-800 w-16 shadow-sm">
                    <div class="typing-dots flex justify-center items-center gap-1">
                        <span class="w-1.5 h-1.5 bg-ocean rounded-full animate-bounce"></span>
                        <span class="w-1.5 h-1.5 bg-ocean rounded-full animate-bounce [animation-delay:0.2s]"></span>
                        <span class="w-1.5 h-1.5 bg-ocean rounded-full animate-bounce [animation-delay:0.4s]"></span>
                    </div>
                </div>
            </div>`;
        msgContainer.scrollTop = msgContainer.scrollHeight;

        const formData = new FormData();
        formData.append("message", query);
        formData.append("csrfmiddlewaretoken", CSRF_TOKEN);

        fetch("/chatbot-response/", { method: "POST", body: formData })
        .then((response) => {
            if (!response.ok) throw new Error("AI server error.");
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            document.getElementById(loaderId)?.remove();

            const aiMsgDiv = document.createElement("div");
            aiMsgDiv.className = "flex justify-start mb-4";
            aiMsgDiv.innerHTML = `<div class="ai-bubble bg-white dark:bg-slate-800 p-4 rounded-2xl rounded-tl-none border border-sky/5 dark:border-slate-800 text-navy dark:text-slate-300 shadow-sm leading-relaxed max-w-[90%] text-sm"></div>`;
            msgContainer.appendChild(aiMsgDiv);
            const bubbleContent = aiMsgDiv.querySelector('.ai-bubble');

            let fullContent = "";
            function read() {
                return reader.read().then(({ done, value }) => {
                    if (done) return;
                    const chunk = decoder.decode(value, { stream: true });
                    chunk.split("\n\n").forEach(line => {
                        if (line.startsWith("data: ")) {
                            try {
                                const jsonStr = line.replace("data: ", "").trim();
                                const data = JSON.parse(jsonStr);
                                if (data.text) {
                                    fullContent += data.text;
                                    bubbleContent.innerHTML = marked.parse(fullContent);
                                    msgContainer.scrollTop = msgContainer.scrollHeight;
                                }
                            } catch (e) { console.error("Parse error", e); }
                        }
                    });
                    return read();
                });
            }
            return read();
        })
        .catch((error) => {
            document.getElementById(loaderId)?.remove();
            msgContainer.innerHTML += `<div class="text-red-500 italic p-2 text-xs text-center mb-4">${error.message}</div>`;
            msgContainer.scrollTop = msgContainer.scrollHeight;
        });
    });

    // --- 7. Projects "View More/Less" Logic (MOVE INSIDE DOMContentLoaded) ---
    const viewMoreBtn = document.getElementById('view-more-projects');
    const viewLessBtn = document.getElementById('view-less-projects');

    if (viewMoreBtn && viewLessBtn) {
        viewMoreBtn.addEventListener('click', function() {
            const hiddenCards = document.querySelectorAll('.project-card.hidden');
            hiddenCards.forEach(card => {
                card.classList.remove('hidden');
                card.classList.add('animate-fade-in');
                card.dataset.wasHidden = "true";
            });
            viewMoreBtn.classList.add('hidden');
            viewLessBtn.classList.remove('hidden');
        });

        viewLessBtn.addEventListener('click', function() {
            const cardsToHide = document.querySelectorAll('.project-card[data-was-hidden="true"]');
            cardsToHide.forEach(card => {
                card.classList.add('hidden');
                card.classList.remove('animate-fade-in');
            });
            viewLessBtn.classList.add('hidden');
            viewMoreBtn.classList.remove('hidden');
            document.getElementById('projects').scrollIntoView({ behavior: 'smooth' });
        });
    }
});

// --- Utility Functions ---
window.copyToClipboard = function(text, message) {
    navigator.clipboard.writeText(text).then(() => {
        Swal.fire({ toast: true, position: 'top-end', icon: 'success', title: message, showConfirmButton: false, timer: 2000, timerProgressBar: true });
    });
}

window.toggleChat = function() {
    const windowEl = document.getElementById("ai-chat-window");
    const bubble = document.getElementById("chat-bubble");
    if (windowEl?.classList.contains("hidden")) {
        windowEl.classList.remove("hidden");
        bubble?.classList.remove("animate-pulse-slow");
        setTimeout(() => windowEl.classList.remove("scale-95", "opacity-0"), 10);
    } else {
        windowEl?.classList.add("scale-95", "opacity-0");
        bubble?.classList.add("animate-pulse-slow");
        setTimeout(() => windowEl?.classList.add("hidden"), 300);
    }
}

window.sendQuickQuery = function(queryText) {
    const input = document.getElementById("ai-user-input");
    const form = document.getElementById("ai-chat-form");
    
    if (input && form) {
        input.value = queryText;
        form.dispatchEvent(new Event('submit'));
    }
};
