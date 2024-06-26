// Function to initialize the chat with a delayed bot message
function initializeChat() {
    setTimeout(function() {
        const chatBody = document.getElementById('chat-body');
        if (!chatBody) {
            console.error('Chat body element not found');
            return;
        }

        // Create and append initial bot message
        const botMessage = createBotMessage("Hello there! How can I assist you today?");
        chatBody.appendChild(botMessage);

        // Scroll to the bottom of the chat after initial message
        chatBody.scrollTop = chatBody.scrollHeight;
    }, 1000); // 1000 milliseconds = 1 second
}

// Function to create bot messages
function createBotMessage(messageContent) {
    const botMessage = document.createElement('div');
    botMessage.classList.add('message', 'bot-message');
    botMessage.innerHTML = `
        <div class="message-content">
            <div class="bot-svg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#b5afaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-robot">
                    <path d="M16 8V4a4 4 0 1 0-8 0v4"></path>
                    <rect x="3" y="8" width="18" height="12" rx="2"></rect>
                    <path d="M7 18v-4a4 4 0 0 1 8 0v4"></path>
                </svg>
            </div>
            <div class="bot-text">
                <p>${messageContent}</p>
            </div>
        </div>
    `;
    return botMessage;
}

// Function to create user messages
function createUserMessage(messageContent) {
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user-message');
    userMessage.innerHTML = `
        <div class="message-content">
            <div class="user-svg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#b5afaf" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-user">
                    <path d="M20.88 18.09A10 10 0 1 0 12 22a9.71 9.71 0 0 0 8.88-3.91"></path>
                    <path d="M12 12a5 5 0 1 0-5-5 5 5 0 0 0 5 5z"></path>
                </svg>
            </div>
            <div class="user-text">
                <p>${messageContent}</p>
            </div>
        </div>
    `;
    return userMessage;
}

// Event listeners for sending messages via button click and Enter key press
function addEventListeners() {
    const sendButton = document.getElementById('send-button');
    const chatInput = document.getElementById('chat-input');

    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    if (chatInput) {
        chatInput.addEventListener('keydown', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }
}

// Function to send user messages and receive bot responses
function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');

    if (!chatInput || !chatBody) {
        console.error('Chat input or chat body element not found');
        return;
    }

    const message = chatInput.value.trim();

    if (message) {
        // Create and append user message using the createUserMessage function
        const userMessage = createUserMessage(message);
        chatBody.appendChild(userMessage);

        // Scroll to the bottom of the chat after sending user message
        chatBody.scrollTop = chatBody.scrollHeight;

        // Fetch bot response from backend
        fetch('/send-message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => response.json())
        .then(data => {
            const botResponse = data.response;

            // Create and append bot message using the createBotMessage function
            const botMessage = createBotMessage(botResponse);
            chatBody.appendChild(botMessage);

            // Scroll to the bottom of the chat after bot response
            chatBody.scrollTop = chatBody.scrollHeight;
        })
        .catch(error => console.error('Error:', error));

        // Clear input after sending message
        chatInput.value = '';
    }
}

// Initialize the chat when the page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeChat();
    addEventListeners();
});
