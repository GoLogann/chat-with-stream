from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["frontend"])

@router.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="utf-8"/>
        <title>Chat With Stream</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
        <style>
            :root {
                --primary-start: #667eea;
                --primary-end: #764ba2;
                --bg-color: #f7f9fc;
                --text-dark: #2d3748;
                --text-light: #718096;
                --border-color: #e2e8f0;
                --white-alpha: rgba(255, 255, 255, 0.85);
            }

            * { margin: 0; padding: 0; box-sizing: border-box; }
            
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: var(--bg-color);
                min-height: 100vh;
                color: var(--text-dark);
                line-height: 1.6;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                flex-direction: column;
            }

            .header {
                background: var(--white-alpha);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                border: 1px solid var(--border-color);
            }

            .header h2 {
                font-weight: 700;
                font-size: 28px;
                background: linear-gradient(135deg, var(--primary-start), var(--primary-end));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 16px;
            }

            .user-controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
            .user-controls label { font-weight: 500; color: var(--text-light); }
            .user-controls input {
                padding: 10px 16px;
                border: 1px solid var(--border-color);
                border-radius: 12px;
                font-size: 14px;
                transition: all 0.3s ease;
                background: white;
                min-width: 200px;
            }
            .user-controls input:focus {
                outline: none;
                border-color: var(--primary-start);
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }

            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .btn-primary {
                background: linear-gradient(135deg, var(--primary-start), var(--primary-end));
                color: white;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2);
            }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(102, 126, 234, 0.3); }

            .main-content { display: flex; gap: 24px; flex: 1; min-height: 0; }
            
            .sidebar {
                width: 320px;
                flex-shrink: 0;
                background: var(--white-alpha);
                backdrop-filter: blur(10px);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                border: 1px solid var(--border-color);
                display: flex;
                flex-direction: column;
            }
            .sidebar h3 {
                color: var(--text-dark);
                margin-bottom: 8px;
                font-weight: 600;
                font-size: 18px;
                padding-bottom: 8px;
                border-bottom: 1px solid var(--border-color);
            }
            .sidebar-controls { margin-bottom: 16px; }
            
            .btn-new-chat {
                width: 100%;
                background: #fff;
                color: var(--primary-start);
                border: 1px solid var(--primary-start);
            }
            .btn-new-chat:hover { background: #f5f7ff; }

            .chat-list { display: flex; flex-direction: column; gap: 8px; overflow-y: auto; flex: 1; padding-right: 5px;}
            .chat-list-item {
                background: #fff;
                color: var(--text-light);
                border: 1px solid var(--border-color);
                width: 100%;
                text-align: left;
            }
            .chat-list-item:hover { background: #f5f7ff; transform: translateY(-1px); }
            .chat-list-item.active {
                border-color: var(--primary-start);
                background: #f5f7ff;
                color: var(--text-dark);
            }
            .chat-list-item strong {
                display: block;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .chat-list-item small { font-size: 12px; }

            .chat-container {
                flex: 1; display: flex; flex-direction: column;
                background: var(--white-alpha); backdrop-filter: blur(10px);
                border-radius: 16px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
                border: 1px solid var(--border-color); overflow: hidden;
            }
            #chat {
                flex: 1; padding: 24px; overflow-y: auto;
                background: white; display: flex; flex-direction: column;
                gap: 16px;
            }
            .message {
                max-width: 85%; padding: 12px 20px; border-radius: 18px;
                font-size: 15px; word-wrap: break-word;
                animation: slideIn 0.3s ease-out;
            }
            @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            
            .msg-user { background: linear-gradient(135deg, var(--primary-start), var(--primary-end)); color: white; align-self: flex-end; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2); }
            .msg-ai { background: #f1f5f9; color: var(--text-dark); align-self: flex-start; border: 1px solid var(--border-color); }
            
            .controls { padding: 16px 24px; background: rgba(248, 250, 252, 0.8); border-top: 1px solid var(--border-color); display: flex; gap: 12px; align-items: center; }
            #question { flex: 1; padding: 14px 20px; border: 1px solid var(--border-color); border-radius: 25px; font-size: 15px; background: white; transition: all 0.3s ease; }
            #question:focus { border-color: var(--primary-start); box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }
            
            .send-btn { padding: 12px 20px; border-radius: 25px; }

            .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-light); font-size: 18px; text-align: center; }
            
            .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-left: 8px; transition: all 0.3s ease; }
            .status-connected { background: #48bb78; box-shadow: 0 0 8px #48bb78; }
            .status-disconnected { background: #f56565; }

            .typing-indicator {
                display: none; padding: 16px 20px; background: #f1f5f9;
                border-radius: 18px; border: 1px solid var(--border-color);
                align-self: flex-start; margin-left: 8px;
                margin-bottom: 10px; /* Ajuste de alinhamento vertical */
            }
            .typing-dots { display: flex; gap: 4px; align-items: center; }
            .typing-dots span { width: 8px; height: 8px; background: #cbd5e0; border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

            /* Ajustes de fonte para Markdown */
            .msg-ai p, .msg-ai li { font-size: 0.95em; }
            .msg-ai h1, .msg-ai h2, .msg-ai h3 { font-size: 1.1em; margin-top: 0.5em; margin-bottom: 0.5em; }
            .message p { margin-bottom: 0.5em; }
            .message p:last-child { margin-bottom: 0; }
            .message ul, .message ol { margin: 0.5em 0 1em 1.5em; }
            .message pre { background-color: #e2e8f0; padding: 16px; border-radius: 8px; margin: 1em 0; overflow-x: auto; font-family: 'Courier New', Courier, monospace; font-size: 0.9em;}
            .message code { background-color: #e2e8f0; padding: 2px 5px; border-radius: 4px; font-size: 0.9em;}
            .message pre code { background-color: transparent; padding: 0; }
            .msg-user code, .msg-user pre { background-color: rgba(255,255,255,0.2); }

            footer { text-align: center; padding: 20px; color: var(--text-light); font-size: 14px; }

            @media (max-width: 992px) {
                .sidebar { width: 280px; }
            }

            @media (max-width: 768px) {
                .container { padding: 10px; }
                .main-content { flex-direction: column; }
                .sidebar { width: 100%; max-height: 35vh; } /* Altura máxima para evitar sobreposição */
                .chat-list-item { padding: 8px 12px; }
                .chat-list-item strong { font-size: 0.9em; }
                .chat-list-item small { font-size: 0.75em; }
                .header h2 { font-size: 24px; }
                .user-controls { gap: 8px; }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header class="header">
                <h2>Chat With Stream</h2>
                <div class="user-controls">
                    <label for="userId">User ID:</label>
                    <input id="userId" value="user-123" />
                    <button class="btn btn-primary" onclick="loadChats()">Carregar Chats</button>
                    <span id="wsStatus" class="status-indicator status-disconnected" title="WebSocket Status"></span>
                </div>
            </header>
            <main class="main-content">
                <aside class="sidebar">
                    <h3>Conversas</h3>
                    <div class="sidebar-controls">
                         <button class="btn btn-new-chat" onclick="startNewChat()">✨ Novo Chat</button>
                    </div>
                    <div id="chats" class="chat-list">
                        <div style="color: var(--text-light); text-align: center; padding: 20px;">
                            Carregue os chats para começar
                        </div>
                    </div>
                </aside>
                <section class="chat-container">
                    <div id="chat">
                        <div class="empty-state">Selecione uma conversa ou inicie uma nova.</div>
                    </div>
                    <div class="typing-indicator" id="typingIndicator">
                        <div class="typing-dots"><span></span><span></span><span></span></div>
                    </div>
                    <div class="controls">
                        <input id="question" placeholder="Digite sua pergunta..." />
                        <button class="btn btn-primary send-btn" onclick="sendMessage()">Enviar ✈️</button>
                    </div>
                </section>
            </main>
            <footer>
                <p>Created by Logan Cardoso</p>
            </footer>
        </div>

        <script>
            let ws = null;
            let currentChatId = null;
            let currentSessionId = null;
            let userId = document.getElementById("userId").value;
            const wsStatus = document.getElementById("wsStatus");

            document.getElementById("question").addEventListener("keypress", (e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage();
                }
            });

            function updateWSStatus(connected) {
                wsStatus.className = `status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`;
                wsStatus.title = connected ? 'WebSocket Conectado' : 'WebSocket Desconectado';
            }
            
            function startNewChat() {
                currentChatId = null;
                currentSessionId = null;
                document.getElementById("chat").innerHTML = '<div class="empty-state">Envie uma mensagem para começar a conversar.</div>';
                document.querySelectorAll('.chat-list-item').forEach(btn => btn.classList.remove('active'));
                document.getElementById('question').focus();
            }

            async function refreshChatList() {
                const chatListContainer = document.getElementById("chats");
                try {
                    const res = await fetch(`/api/chats/${userId}`);
                    const data = await res.json();
                    
                    chatListContainer.innerHTML = "";
                    
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(chat => {
                            const btn = document.createElement("button");
                            btn.className = "btn chat-list-item";
                            btn.dataset.chatId = chat.chat_id;
                            // Prepara o frontend para receber o título do backend
                            btn.innerHTML = `<strong>${chat.title || 'Novo Chat'}</strong><br><small>${new Date(chat.updated_at).toLocaleString()}</small>`;
                            btn.onclick = () => openChat(chat.chat_id);
                            chatListContainer.appendChild(btn);
                        });
                        // Mantém o chat atual ativo visualmente
                        if(currentChatId) {
                            const activeBtn = document.querySelector(`.chat-list-item[data-chat-id="${currentChatId}"]`);
                            if(activeBtn) activeBtn.classList.add('active');
                        }
                    } else {
                        chatListContainer.innerHTML = "<div style='color: var(--text-light); text-align: center; padding: 20px;'>Nenhum chat encontrado</div>";
                    }
                } catch (error) {
                    console.error("Erro ao atualizar lista de chats:", error);
                }
            }
            
            async function loadChats() {
                userId = document.getElementById("userId").value;
                if (!userId) {
                    alert("Por favor, insira um User ID.");
                    return;
                }
                const chatListContainer = document.getElementById("chats");
                chatListContainer.innerHTML = "<p>Carregando...</p>";
                await refreshChatList(); // Usa a função de refresh
                connectWS();
                startNewChat();
            }

            async function openChat(chatId) {
                currentChatId = chatId;
                currentSessionId = null;
                
                document.querySelectorAll('.chat-list-item').forEach(btn => {
                    btn.classList.toggle('active', btn.dataset.chatId === chatId);
                });

                const chatBox = document.getElementById("chat");
                chatBox.innerHTML = "<p>Carregando mensagens...</p>";

                try {
                    const res = await fetch(`/api/chats/${chatId}/messages`);
                    const data = await res.json();
                    
                    chatBox.innerHTML = "";
                    
                    if (data.items && data.items.length > 0) {
                        data.items.forEach(m => {
                            const div = document.createElement("div");
                            div.className = `message ${m.role === "user" ? "msg-user" : "msg-ai"}`;
                            div.innerHTML = marked.parse(m.content);
                            chatBox.appendChild(div);
                        });
                    } else {
                        chatBox.innerHTML = '<div class="empty-state">Este chat ainda não possui mensagens.</div>';
                    }
                    
                    chatBox.scrollTop = chatBox.scrollHeight;
                } catch (error) {
                    console.error("Erro ao abrir chat:", error);
                    chatBox.innerHTML = '<div class="empty-state" style="color: #f56565;">Erro ao carregar mensagens.</div>';
                }
            }

            function connectWS() {
                if (ws && ws.readyState === WebSocket.OPEN) { ws.close(); }
                ws = new WebSocket(`ws://${location.host}/ws/chat/completions`);
                
                ws.onopen = () => { console.log("WS conectado"); updateWSStatus(true); };
                ws.onclose = () => { console.log("WS fechado"); updateWSStatus(false); };
                ws.onerror = (error) => { console.error("Erro WS:", error); updateWSStatus(false); };
                
                ws.onmessage = (event) => {
                    const data = JSON.parse(event.data);
                    const chatBox = document.getElementById("chat");
                    const typingIndicator = document.getElementById("typingIndicator");
                    
                    if (data.type === "start") {
                        currentSessionId = data.session_id;
                        if (!currentChatId) currentChatId = data.chat_id;
                        typingIndicator.style.display = "flex";
                    }
                    else if (data.type === "token") {
                        typingIndicator.style.display = "none";
                        let lastMsg = chatBox.querySelector('.msg-ai:last-child');
                        if (!lastMsg || lastMsg.dataset.sessionId !== currentSessionId) {
                            lastMsg = document.createElement("div");
                            lastMsg.className = "message msg-ai";
                            lastMsg.dataset.rawText = ""; 
                            lastMsg.dataset.sessionId = currentSessionId;
                            chatBox.appendChild(lastMsg);
                        }
                        lastMsg.dataset.rawText += data.text;
                        lastMsg.innerHTML = marked.parse(lastMsg.dataset.rawText);
                        chatBox.scrollTop = chatBox.scrollHeight;
                    }
                    else if (data.type === "end") {
                        typingIndicator.style.display = "none";
                        // Apenas atualiza a lista de chats, sem reconectar
                        if (!document.querySelector(`.chat-list-item[data-chat-id="${currentChatId}"]`)) {
                            refreshChatList();
                        }
                    }
                    else if (data.type === "error") {
                        typingIndicator.style.display = "none";
                        alert("Erro: " + data.message);
                    }
                };
            }

            function sendMessage() {
                const qInput = document.getElementById("question");
                const q = qInput.value.trim();
                if (!q) return;
                if (!ws || ws.readyState !== WebSocket.OPEN) {
                    alert("WebSocket não está conectado! Tentando reconectar...");
                    connectWS();
                    return;
                }
                
                const payload = { user_id: userId, question: q, chat_id: currentChatId, session_id: currentSessionId };
                ws.send(JSON.stringify(payload));
                
                const chatBox = document.getElementById("chat");
                if (chatBox.querySelector('.empty-state')) chatBox.innerHTML = "";
                
                const div = document.createElement("div");
                div.className = "message msg-user";
                div.innerHTML = marked.parse(q);
                chatBox.appendChild(div);
                chatBox.scrollTop = chatBox.scrollHeight;
                qInput.value = "";
                qInput.focus();
            }

            // Inicializa a aplicação
            window.onload = () => {
                loadChats();
            };
        </script>
    </body>
    </html>
    """