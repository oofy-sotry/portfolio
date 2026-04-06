// 고급 AI 챗봇 페이지 (advanced_chat.html)
document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chatMessages');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const faqButtons = document.querySelectorAll('.faq-question');
    const faqWrapper = document.getElementById('faqQuickWrapper');
    const searchModeRadios = document.querySelectorAll('input[name="searchMode"]');

    const providerSelect = document.getElementById('providerSelect');

    let currentMode = 'concise';
    let currentSearchMode = 'faq';

    // 답변 모드 변경
    document.querySelectorAll('input[name="responseMode"]').forEach(radio => {
        radio.addEventListener('change', function() {
            currentMode = this.value;
        });
    });

    // 검색 모드 변경
    function updateFaqVisibility() {
        if (!faqWrapper) return;
        faqWrapper.style.display = (currentSearchMode === 'faq') ? 'block' : 'none';
    }

    searchModeRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            currentSearchMode = this.value;
            updateFaqVisibility();
        });
    });
    updateFaqVisibility();

    function sendMessage() {
        const message = messageInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        messageInput.value = '';
        showTypingIndicator();

        fetch('/chatbot/ai-chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                mode: currentMode,
                search_mode: currentSearchMode,
                provider: providerSelect ? providerSelect.value : 'local'
            })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            if (data.error) {
                addMessage('죄송합니다. 오류가 발생했습니다: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
                if (data.related_docs && data.related_docs.length > 0) {
                    showRelatedDocs(data.related_docs);
                }
            }
        })
        .catch(() => {
            hideTypingIndicator();
            addMessage('죄송합니다. 연결에 문제가 발생했습니다.', 'bot');
        });
    }

    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-3 ${sender}-message`;

        const avatar = sender === 'user' ?
            '<i class="fas fa-user fa-2x text-success"></i>' :
            '<i class="fas fa-robot fa-2x text-primary"></i>';

        const bubbleClass = sender === 'user' ?
            'bg-primary text-white' :
            'bg-white border';

        messageDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="avatar me-3">${avatar}</div>
                <div class="message-content">
                    <div class="message-bubble ${bubbleClass} p-3 rounded">
                        <p class="mb-0">${text}</p>
                        <small class="text-muted">방금 전</small>
                    </div>
                </div>
            </div>
        `;

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'mb-3 bot-message typing-indicator show';
        typingDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="avatar me-3">
                    <i class="fas fa-robot fa-2x text-primary"></i>
                </div>
                <div class="message-content">
                    <div class="message-bubble bg-white border p-3 rounded">
                        <div class="d-flex align-items-center">
                            <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                            <span>답변을 생성하고 있습니다...</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function hideTypingIndicator() {
        const indicator = chatMessages.querySelector('.typing-indicator');
        if (indicator) indicator.remove();
    }

    function showRelatedDocs(docs) {
        const docsDiv = document.createElement('div');
        docsDiv.className = 'mb-3 bot-message';
        docsDiv.innerHTML = `
            <div class="d-flex align-items-start">
                <div class="avatar me-3">
                    <i class="fas fa-robot fa-2x text-primary"></i>
                </div>
                <div class="message-content">
                    <div class="message-bubble bg-light border p-3 rounded">
                        <h6 class="mb-2">관련 문서:</h6>
                        ${docs.map(doc => {
                            const src = doc._source || {};
                            const title = src.title || '제목 없음';
                            const content = src.summary || (src.content || '').substring(0, 100);
                            const postId = src.post_id;
                            const link = postId ? `/board/${postId}` : '#';
                            return `<div class="mb-2">
                                <a href="${link}" class="text-decoration-none"><strong>${title}</strong></a>
                                <p class="mb-1 small text-muted">${content}...</p>
                            </div>`;
                        }).join('')}
                    </div>
                </div>
            </div>
        `;
        chatMessages.appendChild(docsDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendButton.addEventListener('click', sendMessage);
    messageInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });

    faqButtons.forEach(button => {
        button.addEventListener('click', function() {
            messageInput.value = this.dataset.question;
            sendMessage();
        });
    });
});
