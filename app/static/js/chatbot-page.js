// 일반 챗봇 페이지 (chat.html)
const chatForm = document.getElementById('chat-form');
if (chatForm) {
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();

        const messageInput = document.getElementById('user-message');
        const message = messageInput.value.trim();

        if (!message) return;

        addMessage(message, 'user');
        messageInput.value = '';
        showTypingIndicator();

        fetch('/chatbot/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            if (data.error) {
                addMessage('죄송합니다. 오류가 발생했습니다: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(() => {
            hideTypingIndicator();
            addMessage('죄송합니다. 연결에 문제가 발생했습니다.', 'bot');
        });
    });

    document.getElementById('user-message').addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event('submit'));
        }
    });
}

function addMessage(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;

    const now = new Date();
    const timeString = now.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div class="message-content">
            <strong>${sender === 'user' ? '나' : 'AI 챗봇'}:</strong> ${message}
        </div>
        <small class="text-muted">${timeString}</small>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const chatMessages = document.getElementById('chat-messages');
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'message bot-message typing-indicator';
    typingDiv.innerHTML = `
        <div class="message-content">
            <strong>AI 챗봇:</strong> <span class="typing-dots">...</span>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    const dots = typingDiv.querySelector('.typing-dots');
    let dotCount = 0;
    window.typingInterval = setInterval(() => {
        dotCount = (dotCount + 1) % 4;
        dots.textContent = '.'.repeat(dotCount);
    }, 500);
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) indicator.remove();
    if (window.typingInterval) clearInterval(window.typingInterval);
}

// FAQ 페이지에서 질문 클릭 시 챗봇으로 이동
function askQuestion(question) {
    const chatUrl = document.body.dataset.chatUrl || '/chatbot/';
    window.location.href = `${chatUrl}?q=${encodeURIComponent(question)}`;
}
