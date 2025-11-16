// Chatbot JavaScript

document.addEventListener('DOMContentLoaded', function() {
    const chatbotToggle = document.getElementById('chatbotToggle');
    const chatbotModal = document.getElementById('chatbotModal');
    const chatbotClose = document.getElementById('chatbotClose');
    const chatInput = document.getElementById('chatInput');
    const chatSend = document.getElementById('chatSend');
    const chatMessages = document.getElementById('chatMessages');

    // Toggle chatbot modal
    if (chatbotToggle && chatbotModal) {
        chatbotToggle.addEventListener('click', function() {
            chatbotModal.classList.toggle('show');
            if (chatbotModal.classList.contains('show')) {
                chatInput.focus();
            }
        });

        chatbotClose.addEventListener('click', function() {
            chatbotModal.classList.remove('show');
        });

        // Close modal when clicking outside
        document.addEventListener('click', function(e) {
            if (!chatbotModal.contains(e.target) && !chatbotToggle.contains(e.target)) {
                chatbotModal.classList.remove('show');
            }
        });
    }

    // Send message functionality
    if (chatSend && chatInput) {
        chatSend.addEventListener('click', sendMessage);
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        chatInput.value = '';

        // Show loading indicator
        const loadingMessage = addMessage('답변을 생성하고 있습니다...', 'bot', true);
        
        // Send message to server
        fetch('/chatbot/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            // Remove loading message
            loadingMessage.remove();
            
            if (data.error) {
                addMessage('죄송합니다. 오류가 발생했습니다: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            // Remove loading message
            loadingMessage.remove();
            addMessage('죄송합니다. 연결에 문제가 발생했습니다.', 'bot');
            console.error('Error:', error);
        });
    }

    function addMessage(text, sender, isLoading = false) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `${sender}-message`;
        
        if (isLoading) {
            messageDiv.innerHTML = `
                <i class="fas fa-robot"></i>
                <span class="spinner"></span> ${text}
            `;
        } else {
            const icon = sender === 'user' ? 'fas fa-user' : 'fas fa-robot';
            messageDiv.innerHTML = `
                <i class="${icon}"></i>
                ${text}
            `;
        }
        
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        
        return messageDiv;
    }

    // Auto-resize textarea
    if (chatInput) {
        chatInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = this.scrollHeight + 'px';
        });
    }

    // Quick reply buttons
    const quickReplies = [
        '자기소개',
        '기술스택',
        '프로젝트',
        '연락처',
        '경력'
    ];

    // Add quick reply buttons to initial message
    function addQuickReplies() {
        const quickReplyDiv = document.createElement('div');
        quickReplyDiv.className = 'quick-replies mt-3';
        quickReplyDiv.innerHTML = '<small class="text-muted">빠른 질문:</small>';
        
        quickReplies.forEach(reply => {
            const button = document.createElement('button');
            button.className = 'btn btn-sm btn-outline-primary me-2 mb-2';
            button.textContent = reply;
            button.addEventListener('click', function() {
                chatInput.value = reply;
                sendMessage();
            });
            quickReplyDiv.appendChild(button);
        });
        
        chatMessages.appendChild(quickReplyDiv);
    }

    // Add quick replies when chatbot is first opened
    let isFirstOpen = true;
    if (chatbotToggle) {
        chatbotToggle.addEventListener('click', function() {
            if (isFirstOpen && chatbotModal.classList.contains('show')) {
                setTimeout(addQuickReplies, 500);
                isFirstOpen = false;
            }
        });
    }

    // Typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'bot-message typing-indicator';
        typingDiv.innerHTML = `
            <i class="fas fa-robot"></i>
            <span class="typing-dots">
                <span>.</span><span>.</span><span>.</span>
            </span>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return typingDiv;
    }

    function hideTypingIndicator(typingDiv) {
        if (typingDiv) {
            typingDiv.remove();
        }
    }

    // Enhanced send message with typing indicator
    const originalSendMessage = sendMessage;
    sendMessage = function() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage(message, 'user');
        chatInput.value = '';

        // Show typing indicator
        const typingIndicator = showTypingIndicator();
        
        // Send to server
        fetch('/chatbot/send', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator(typingIndicator);
            
            if (data.error) {
                addMessage('죄송합니다. 오류가 발생했습니다: ' + data.error, 'bot');
            } else {
                addMessage(data.response, 'bot');
            }
        })
        .catch(error => {
            hideTypingIndicator(typingIndicator);
            addMessage('죄송합니다. 연결에 문제가 발생했습니다.', 'bot');
            console.error('Error:', error);
        });
    };
});

// CSS for typing indicator
const style = document.createElement('style');
style.textContent = `
    .typing-indicator {
        opacity: 0.7;
    }
    
    .typing-dots {
        display: inline-block;
    }
    
    .typing-dots span {
        animation: typing 1.4s infinite;
        animation-delay: calc(var(--i) * 0.2s);
    }
    
    .typing-dots span:nth-child(1) { --i: 0; }
    .typing-dots span:nth-child(2) { --i: 1; }
    .typing-dots span:nth-child(3) { --i: 2; }
    
    @keyframes typing {
        0%, 60%, 100% {
            opacity: 0.3;
        }
        30% {
            opacity: 1;
        }
    }
    
    .quick-replies {
        border-top: 1px solid #dee2e6;
        padding-top: 10px;
    }
    
    .quick-replies button {
        font-size: 0.8rem;
        padding: 4px 8px;
    }
`;
document.head.appendChild(style);
