/* scripts.js */

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Verifica se o cookie possui o prefixo correto
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Função para calcular e ajustar a posição do chatbox em relação ao headerpage
function adjustChatboxPosition() {
    const headerpageHeight = document.querySelector('.headerpage').offsetHeight;
    const allchat = document.querySelector('.allchat');
    allchat.style.top = headerpageHeight + 40 + 'px';
}

// Chama a função ao carregar a página e redimensionar a janela
window.addEventListener('DOMContentLoaded', adjustChatboxPosition);
window.addEventListener('resize', adjustChatboxPosition);

const form = document.getElementById('chat-form');
const messageInput = document.getElementById('message');
const chatMessages = document.getElementById('chat-messages');

form.addEventListener('submit', function (event) {
    event.preventDefault(); // Evita o recarregamento da página

    const messageText = messageInput.value;
    if (messageText.trim() !== '') {
        appendMessage('Você', messageText); // Adiciona a mensagem enviada pelo usuário
        $.get('/chatbot/process-message',{usermessage:messageText}).done(function(data){
            chatMessages.appendChild(
            `<div class="botmensage">
            <span>BOT:</span>
            <span class="bot-talk">${data}</span>
            <div class="bot-icon">
                <img src="/static/images/bot.png" alt="">
            </div>
            </div>`);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        });

        // Manter a rolagem automática para exibir a última mensagem
        chatMessages.scrollTop = chatMessages.scrollHeight;
        messageInput.value = ''; // Limpa o campo de entrada após o envio da mensagem
    }
});

function appendMessage(user, text) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.innerHTML = `<span class="user">${user}:</span> <span class="text">${text}</span>;`
    chatMessages.appendChild(messageElement);

    // Manter a rolagem automática para exibir a última mensagem
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

//<script src="{% static 'scripts/script.js' %}"></script>