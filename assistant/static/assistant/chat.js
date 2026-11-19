document.addEventListener("DOMContentLoaded", function () {
    const widget = document.getElementById("chat-widget");

    if (!widget) {
        return;
    }

    const toggle = document.getElementById("chat-toggle");
    const panel = document.getElementById("chat-panel");
    const closeButton = document.getElementById("chat-close");
    const messages = document.getElementById("chat-messages");
    const form = document.getElementById("chat-form");
    const question = document.getElementById("chat-question");
    const sendButton = document.getElementById("chat-send");

    let waiting = false;
    let historyLoaded = false;

    async function loadHistory() {  // earlier questions about this analysis
        if (historyLoaded || !widget.dataset.historyUrl) {
            return;
        }

        historyLoaded = true;

        try {
            const response = await fetch(widget.dataset.historyUrl);

            if (!response.ok) {
                return;
            }

            const data = await response.json();
            const newMessages = Array.from(messages.children).slice(1);  // sent while this was loading

            data.messages.forEach(function (message) {
                addMessage(message.content, message.role);
            });
            newMessages.forEach(function (message) {
                messages.appendChild(message);
            });
            messages.scrollTop = messages.scrollHeight;
        } catch (error) {
            historyLoaded = false;  // the chat still works; try again next time it opens
        }
    }

    function setOpen(open) {
        panel.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
        toggle.setAttribute("aria-label", open ? "Close assistant" : "Open assistant");

        if (open) {
            question.focus();
            loadHistory();
        } else {
            toggle.focus();
        }
    }

    // always textContent: questions and answers must never run as HTML
    function addMessage(text, type) {
        const message = document.createElement("div");
        message.className = `chat-message chat-message-${type}`;
        message.textContent = text;
        messages.appendChild(message);
        messages.scrollTop = messages.scrollHeight;
        return message;
    }

    function addSources(message, sources) {
        if (!sources || sources.length === 0) {
            return;
        }

        const element = document.createElement("span");
        element.className = "chat-sources";
        element.textContent = `Source: ${sources.join(", ")}`;
        message.appendChild(element);
    }

    function addRetrieved(message, retrieved) {  // only sent while DEBUG is on
        if (!retrieved) {
            return;
        }

        const details = document.createElement("details");
        details.className = "chat-retrieved";

        const summary = document.createElement("summary");
        summary.textContent = "Retrieved chunks";
        details.appendChild(summary);

        const list = document.createElement("ul");
        retrieved.forEach(function (chunk) {
            const item = document.createElement("li");
            item.textContent = `${chunk.similarity.toFixed(3)}  ${chunk.id}  ${chunk.title}`;
            list.appendChild(item);
        });
        details.appendChild(list);

        message.appendChild(details);
    }

    async function sendQuestion() {
        const text = question.value.trim();

        if (!text || waiting) {
            return;
        }

        // FormData carries the CSRF token from the form
        const formData = new FormData(form);

        waiting = true;
        sendButton.disabled = true;
        question.value = "";
        addMessage(text, "user");
        const pending = addMessage("Thinking...", "assistant");
        pending.classList.add("chat-message-pending");

        try {
            const response = await fetch(widget.dataset.chatUrl, {
                method: "POST",
                body: formData,
            });
            const data = await response.json();
            pending.remove();

            if (response.ok) {
                const message = addMessage(data.answer, "assistant");
                addSources(message, data.sources);
                addRetrieved(message, data.retrieved);
                messages.scrollTop = messages.scrollHeight;
            } else {
                addMessage(data.error, "error");
            }
        } catch (error) {
            pending.remove();
            addMessage("Something went wrong. Please refresh the page and try again.", "error");
        } finally {
            waiting = false;
            sendButton.disabled = false;
            question.focus();
        }
    }

    toggle.addEventListener("click", function () {
        setOpen(panel.hidden);
    });

    closeButton.addEventListener("click", function () {
        setOpen(false);
    });

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        sendQuestion();
    });

    question.addEventListener("keydown", function (event) {
        // Enter sends, Shift+Enter adds a line; isComposing keeps Enter for the Chinese input method
        if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
            event.preventDefault();
            sendQuestion();
        }
    });

    // only when focus is in the chat, so Esc does not also close it from other pop-ups
    panel.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {
            setOpen(false);
        }
    });
});
