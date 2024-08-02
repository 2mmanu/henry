let sessionId = null;
let sentinelCalled = false;
const apiUrl = 'http://localhost:8001/api/v1';
const apiSession = 'http://localhost:8002/api/v1';

const chatContainer = document.getElementById('chat-container');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');

async function callSentinel() {
    sentinelCalled = true;
    try {
        const response = await fetch(`${apiUrl}/sentinel`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Session-Id': sessionId
            },
        });
        const data = await response.text();
        console.log('Sentinel Response:', data);

    } catch (error) {
        console.error('Error calling sentinel:', error);
        sentinelCalled = false;
    }
}

async function createSession() {
    try {
        const response = await fetch(`${apiSession}/create-session`, {
            method: 'POST',
            headers: {
                'accept': 'application/json',
            }
        });
        const data = await response.json();
        sessionId = data.sessionId;
        console.log('Session ID:', sessionId);
        // startEventSource();
    } catch (error) {
        console.error('Errore nella creazione della sessione:', error);
    }
    askUsername();
}

async function closeSession(sessionId) {
    try {
        const response = await fetch(`${apiSession}/close-session`, {
            method: 'POST',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json' // Specify that we're sending JSON
            },
            body: JSON.stringify({
                'sessionId': sessionId
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const data = await response.json();
        console.log('Status:', data.status);
    } catch (error) {
        console.error('Error closing session:', error);
    }
}

function showWaitingMessage(show) {
    const waitingMessage = document.getElementById('waiting-message');
    waitingMessage.style.display = show ? 'block' : 'none';
}

async function sendMessage(message) {
    try {
        addMessageToChat(message, 'sent');
        showWaitingMessage(true);

        console.log("Question: ", message)

        const url = `${apiUrl}/stream?sessionId=${encodeURIComponent(sessionId)}&content=${encodeURIComponent(message)}`;
        const eventSource = new EventSource(url);

        eventSource.onmessage = function (event) {
            const data = JSON.parse(event.data);

            if (data.messages) {
                data.messages.forEach(message => {
                    if (message.internal_monologue) {
                        console.log("Internal Monologue:", message.internal_monologue);
                    } else if (message.function_call) {
                        try {
                            const functionArguments = JSON.parse(message.function_call.arguments);
                            console.log(`Function Call (${message.function_call.name}):`, functionArguments);
                            if (message.function_call.name == 'send_message') {
                                addMessageToChat(functionArguments.message, 'received');
                            }
                        } catch (error) {
                            console.log("Function Call:", message.function_call);
                        }
                    } else if (message.function_return) {
                        console.log("Function Return:", message.function_return);
                    } else {
                        console.log("Message:", message);
                    }
                });
            }

            if (data.usage) {
                console.log("Usage data:", data.usage);
            }

            showWaitingMessage(false);
            eventSource.close();
        };

        // eventSource.onerror = function (event) {
        //     console.error("EventSource failed:", event);
        //     eventSource.close();
        // };

        // const eventSource = new EventSource(`${apiUrl}/stream?sessionId=${encodeURIComponent(sessionId)}&content=${encodeURIComponent(message)}`);

        // eventSource.onmessage = function (event) {
        //     const data = JSON.parse(event);
        //     console.log("New message:", data);
        //     // const data = JSON.parse(event.data);
        //     // console.log('Received:', data);
        //     // addMessageToChat(data.messages, 'received');
        //     // showWaitingMessage(false);
        //     // eventSource.close();
        // };

        // eventSource.onerror = function (event) {
        //     console.error("EventSource failed:", event);
        //     eventSource.close();
        // };

    } catch (error) {
        console.error('Error sending message:', error);
    }
}

function addMessageToChat(message, type) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', type);
    messageElement.textContent = message;
    chatContainer.appendChild(messageElement);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    setTimeout(() => {
        messageElement.classList.add('visible');
    }, 10);
}

function startEventSource() {
    const eventSource = new EventSource(`${apiUrl}/stream?sessionId=${encodeURIComponent(sessionId)}`);

    eventSource.onmessage = function (event) {
        console.log('Received:', event.data);
        addMessageToChat(event.data, 'received');
    };

    window.addEventListener('beforeunload', () => {
        eventSource.close();
    });
}

async function askUsername() {
    const username = prompt("Please enter your name:", "00000000-0000-0000-0000-000000375016");
    if (username) {
        // document.getElementById('username').textContent = username;
        try {
            const response = await fetch(`${apiUrl}/set-username`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Session-Id': sessionId,
                },
                body: JSON.stringify({
                    'username': username,
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to set username');
            }
        } catch (error) {
            console.error('Error setting username:', error);
        }
    }
}


sendButton.addEventListener('click', () => {
    const message = messageInput.value.trim();
    if (message) {
        sendMessage(message);
        messageInput.value = '';
    }
});

messageInput.addEventListener('keydown', (event) => {
    if (!sentinelCalled) {
        callSentinel();
    }
    if (event.key === 'Enter' && !event.altKey) {
        event.preventDefault();
        const message = messageInput.value.trim();
        if (message) {
            sendMessage(message);
            messageInput.value = '';
        }
    }
});

window.addEventListener('beforeunload', () => {
    if (sessionId) {
        closeSession(sessionId);
    }
});

document.addEventListener('DOMContentLoaded', (event) => {
    createSession();
    
});


