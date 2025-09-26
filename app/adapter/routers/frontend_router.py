from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["frontend"])

@router.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"/>
        <title>Chat With Stream - Teste</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: #333;
            }
            .container { max-width: 1200px; margin: 0 auto; padding: 20px; min-height: 100vh; display: flex; flex-direction: column; }
            .header {
                background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
                border-radius: 16px; padding: 24px; margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .header h2 {
                color: #2d3748; margin-bottom: 16px; font-weight: 600; font-size: 28px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            }
            .user-controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
            .user-controls label { font-weight: 500; color: #4a5568; }
            .user-controls input {
                padding: 10px 16px; border: 2px solid #e2e8f0; border-radius: 12px; font-size: 14px;
                transition: all 0.3s ease; background: white; min-width: 200px;
            }
            .user-controls input:focus {
                outline: none; border-color: #667eea; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            .btn { padding: 10px 20px; border: none; border-radius: 12px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.3s ease; }
            .btn-primary {
                background: linear-gradient(135deg, #667eea, #764ba2); color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4); }
            .btn-secondary { background: rgba(255, 255, 255, 0.9); color: #4a5568; border: 2px solid #e2e8f0; margin: 4px; }
            .btn-secondary:hover { background: #f7fafc; border-color: #cbd5e0; transform: translateY(-1px); }
            .main-content { display: flex; gap: 24px; flex: 1; min-height: 0; }
            .sidebar {
                width: 320px; background: rgba(255, 255, 255, 0.95); backdrop-filter: blur(10px);
                border-radius: 16px; padding: 24px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1); border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .sidebar h3 { color: #2d3748; margin-bottom: 16px; font-weight: 600; font-size: 18px; }
            .chat-list { display: flex; flex-direction: column; gap: 8px; max-height: 400px; overflow-y: auto; }
            .chat-container {
                flex: 1; display: flex; flex-direction: column; background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px); border-radius: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2); overflow: hidden;
            }
            #chat { flex: 1; padding: 24px; overflow-y: auto; background: #f8fafc; display: flex; flex-direction: column; gap: 16px; }
            .message {
                max-width: 80%; padding: 16px 20px; border-radius: 18px; font-size: 15px; line-height: 1.5;
                word-wrap: break-word; animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px);} to { opacity: 1; transform: translateY(0);} }
            .msg-user { background: linear-gradient(135deg, #667eea, #764ba2); color: white; align-self: flex-end; margin-left: auto; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3); }
            .msg-ai { background: white; color: #2d3748; align-self: flex-start; border: 1px solid #e2e8f0; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1); }
            .msg-ai::before { content: "🤖"; margin-right: 8px; }
            .msg-user::before { content: "👤"; margin-right: 8px; }
            .controls { padding: 24px; background: rgba(255, 255, 255, 0.95); border-top: 1px solid #e2e8f0; display: flex; gap: 12px; align-items: center; }
            #question { flex: 1; padding: 14px 20px; border: 2px solid #e2e8f0; border-radius: 25px; font-size: 15px; background: white; }
            .send-btn {
                padding: 14px 24px; border: none; border-radius: 25px; background: linear-gradient(135deg, #667eea, #764ba2);
                color: white; font-weight: 500; cursor: pointer; transition: all 0.3s ease; display: flex; align-items: center; gap: 8px;
            }
            .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: #a0aec0; font-size: 18px; }
            .status-indicator { display: inline-block; width: 8px; height: 8px; border-radius: 50%; margin-left: 8px; }
            .status-connected { background: #48bb78; box-shadow: 0 0 8px rgba(72, 187, 120, 0.6); }
            .status-disconnected { background: #f56565; }
            .typing-indicator { display: none; padding: 16px 20px; background: white; border-radius: 18px; border: 1px solid #e2e8f0; align-self: flex-start; max-width: 80px; }
            .typing-dots { display: flex; gap: 4px; }
            .typing-dots span {
                width: 8px; height: 8px; background: #cbd5e0; border-radius: 50%;
                animation: bounce 1.4s infinite ease-in-out;
            }
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce { 0%, 80%, 100% { transform: scale(0);} 40% { transform: scale(1);} }

            /* Estilos para o conteúdo Markdown */
            .message p { margin-bottom: 1em; }
            .message p:last-child { margin-bottom: 0; }
            .message ul, .message ol { margin: 0.5em 0 1em 1.5em; }
            .message li { margin-bottom: 0.4em; }
            .message pre { background-color: #e2e8f0; padding: 16px; border-radius: 8px; margin: 1em 0; overflow-x: auto; font-family: 'Courier New', Courier, monospace; }
            .message code { background-color: #e2e8f0; padding: 2px 5px; border-radius: 4px; font-family: 'Courier New', Courier, monospace; }
            .message pre code { background-color: transparent; padding: 0; }
            .message blockquote { border-left: 3px solid #cbd5e0; padding-left: 1em; margin-left: 0; color: #718096; }
            .msg-user code, .msg-user pre { background-color: rgba(0,0,0,0.15); }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Chat With Stream</h2>
                <div class="user-controls">
                    <label>User ID:</label>
                    <input id="userId" value="user-123" />
                    <button class="btn btn-primary" onclick="loadChats()">Carregar Chats</button>
                    <span id="wsStatus" class="status-indicator status-disconnected"></span>
                </div>
            </div>
            <div class="main-content">
                <div class="sidebar">
                    <div id="chats">
                        <h3>Chats</h3>
                        <div class="chat-list">
                            <div style="color: #a0aec0; text-align: center; padding: 20px;">
                                Carregue os chats para começar
                            </div>
                        </div>
                    </div>
                </div>
                <div class="chat-container">
                    <div id="chat">
                        <div class="empty-state">Selecione um chat para começar a conversar</div>
                    </div>
                    <div class="typing-indicator" id="typingIndicator">
                        <div class="typing-dots"><span></span><span></span></div>
                    </div>
                    <div class="controls">
                        <input id="question" placeholder="Digite sua pergunta..." />
                        <button class="send-btn" onclick="sendMessage()">Enviar ✈️</button>
                    </div>
                </div>
            </div>
        </div>
        <script>
            let ws = null;
            let currentChatId = null;
            let currentSessionId = null;
            let userId = document.getElementById("userId").value;
            const wsStatus = document.getElementById("wsStatus");

            document.getElementById("question").addEventListener("keypress", function(e) {
                if (e.key === "Enter") sendMessage();
            });

            function updateWSStatus(connected) {
                wsStatus.className = `status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`;
            }

            async function loadChats() {
                userId = document.getElementById("userId").value;
                try {
                    const res = await fetch(`/api/chats/${userId}`);
                    const data = await res.json();
                    const container = document.getElementById("chats");
                    container.innerHTML = "<h3>Chats</h3><div class='chat-list'></div>";
                    const chatList = container.querySelector('.chat-list');
                    
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(chat => {
                            const btn = document.createElement("button");
                            btn.className = "btn btn-secondary";
                            btn.style.width = "100%";
                            btn.style.textAlign = "left";
                            btn.innerHTML = `<strong>${chat.title}</strong><br><small>${new Date(chat.updated_at).toLocaleString()}</small>`;
                            btn.onclick = () => openChat(chat.chat_id);
                            chatList.appendChild(btn);
                        });
                    } else {
                        chatList.innerHTML = "<div style='color: #a0aec0; text-align: center; padding: 20px;'>Nenhum chat encontrado</div>";
                    }
                } catch (error) {
                    console.error("Erro ao carregar chats:", error);
                }
            }

            async function openChat(chatId) {
                currentChatId = chatId;
                try {
                    const res = await fetch(`/api/chats/${chatId}/messages`);
                    const data = await res.json();
                    const chatBox = document.getElementById("chat");
                    chatBox.innerHTML = "";
                    
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(m => {
                            const div = document.createElement("div");
                            div.className = `message ${m.role === "user" ? "msg-user" : "msg-ai"}`;
                            // Renderiza o conteúdo como Markdown
                            div.innerHTML = marked.parse(m.content);
                            chatBox.appendChild(div);
                        });
                    }
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch (error) {
                    console.error("Erro ao abrir chat:", error);
                }
            }

            function connectWS() {
                if (ws) ws.close();
                ws = new WebSocket(`ws://${location.host}/ws/chat/completions`);
                
                ws.onopen = () => { console.log("WS conectado"); updateWSStatus(true); };
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    const chatBox = document.getElementById("chat");
                    const typingIndicator = document.getElementById("typingIndicator");
                    
                    if (data.type === "start") {
                        currentSessionId = data.session_id;
                        currentChatId = data.chat_id;
                        typingIndicator.style.display = "flex";
                    }
                    else if (data.type === "token") {
                        typingIndicator.style.display = "none";
                        let last = chatBox.lastElementChild;
                        if (!last || !last.classList.contains("msg-ai")) {
                            last = document.createElement("div");
                            last.className = "message msg-ai";
                            // Armazena o texto bruto em um atributo de dados
                            last.dataset.rawText = ""; 
                            chatBox.appendChild(last);
                        }
                        // Acumula o texto bruto e renderiza o markdown completo
                        last.dataset.rawText += data.text;
                        last.innerHTML = marked.parse(last.dataset.rawText);
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                    else if (data.type === "end") {
                        typingIndicator.style.display = "none";
                        console.log("Resposta finalizada.");
                        // Opcional: recarregar a lista de chats se for um novo chat
                        if (!document.querySelector(`[onclick="openChat('${currentChatId}')"]`)) {
                            loadChats();
                        }
                    }
                    else if (data.type === "error") {
                        typingIndicator.style.display = "none";
                        alert("Erro: " + data.message);
                    }
                };
                ws.onclose = () => { console.log("WS fechado"); updateWSStatus(false); };
                ws.onerror = (error) => { console.error("Erro WS:", error); updateWSStatus(false); };
            }

            function sendMessage() {
                const q = document.getElementById("question").value.trim();
                if (!q) return;
                if (!ws || ws.readyState !== WebSocket.OPEN) { alert("WebSocket não conectado!"); return; }
                
                const payload = { user_id: userId, question: q, chat_id: currentChatId, session_id: currentSessionId };
                ws.send(JSON.stringify(payload));
                
                const chatBox = document.getElementById("chat");
                const emptyState = chatBox.querySelector('.empty-state');
                if (emptyState) emptyState.remove();
                
                const div = document.createElement("div");
                div.className = "message msg-user";
                // Renderiza a pergunta do usuário como Markdown também
                div.innerHTML = marked.parse(q);
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
                document.getElementById("question").value = "";
            }

            // Inicializa já conectado e com chats carregados
            loadChats();
            connectWS();
        </script>
    </body>
    </html>
    """