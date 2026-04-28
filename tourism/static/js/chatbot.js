// Chatbot functionality for Mathura Darshan

class ChatbotManager {
    constructor(chatBoxId, inputId) {
        this.chatBox = document.getElementById(chatBoxId);
        this.input = document.getElementById(inputId);
        this.messageHistory = [];
    }

    addMessage(message, sender = 'user') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        messageDiv.textContent = message;
        this.chatBox.appendChild(messageDiv);
        this.chatBox.scrollTop = this.chatBox.scrollHeight;

        this.messageHistory.push({
            message,
            sender,
            timestamp: new Date()
        });
    }

    async sendMessage(message) {
        if (!message.trim()) return;

        this.addMessage(message, 'user');
        this.input.value = '';

        try {
            const response = await fetch('/chatbot/api/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();

            if (data.success) {
                let botResponse = data.response;
                if (data.weather) {
                    botResponse += '\n\n📍 ' + data.weather;
                }
                this.addMessage(botResponse, 'bot');
            } else {
                this.addMessage('Error: ' + (data.error || 'Unknown error'), 'bot');
            }
        } catch (error) {
            console.error('Chatbot error:', error);
            this.addMessage('Connection error. Please try again.', 'bot');
        }
    }

    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    startVoiceInput(callbackFn) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (!SpeechRecognition) {
            alert('Speech Recognition not supported');
            return;
        }

        const recognition = new SpeechRecognition();
        recognition.lang = 'en-IN';

        recognition.onresult = (event) => {
            let transcript = '';
            for (let i = event.resultIndex; i < event.results.length; i++) {
                if (event.results[i].isFinal) {
                    transcript += event.results[i][0].transcript + ' ';
                }
            }
            if (transcript.trim()) {
                if (callbackFn) callbackFn(transcript.trim());
                else this.input.value = transcript.trim();
            }
        };

        recognition.start();
    }

    clearHistory() {
        this.messageHistory = [];
        this.chatBox.innerHTML = '';
    }
}

// Export
window.ChatbotManager = ChatbotManager;
