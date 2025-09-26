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
                --primary-main: #007BFF;
                --primary-light: #58A6FF;
                --bg-color: #F0F8FF;
                --surface-color: #FFFFFF;
                --text-dark: #1A202C;
                --text-light: #6C757D;
                --border-color: #DEE2E6;
                --surface-alpha: rgba(255, 255, 255, 0.9);
                --ai-msg-bg: #E9ECEF;
            }

            * { margin: 0; padding: 0; box-sizing: border-box; }

            html {
                height: 100%;
                overflow: hidden; /* Impede o scroll na página principal */
            }
            
            body {
                height: 100%;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
                background-color: var(--bg-color);
                color: var(--text-dark);
                line-height: 1.6;
                display: flex;
                flex-direction: column;
            }

            .container {
                display: flex;
                flex-direction: column;
                height: 100vh;
                width: 95%; /* AUMENTADO: Usa 95% da largura da tela */
                max-width: 2400px; /* AUMENTADO: Novo limite máximo bem largo */
                margin: 0 auto;
                padding: 15px;
                gap: 15px;
            }

            .header {
                background: var(--surface-alpha);
                backdrop-filter: blur(8px);
                border-radius: 16px;
                padding: 15px 24px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
                border: 1px solid var(--border-color);
                flex-shrink: 0;
            }

            .header h2 {
                font-weight: 700;
                font-size: 26px;
                background: linear-gradient(135deg, var(--primary-main), var(--primary-light));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                margin-bottom: 12px;
            }

            .user-controls { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
            .user-controls label { font-weight: 500; color: var(--text-light); }
            .user-controls input {
                padding: 8px 14px;
                border: 1px solid var(--border-color);
                border-radius: 10px;
                font-size: 14px;
                transition: all 0.2s ease;
                background: white;
                min-width: 180px;
            }
            .user-controls input:focus {
                outline: none;
                border-color: var(--primary-main);
                box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.15);
            }

            .btn {
                padding: 8px 18px;
                border: none;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.2s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 8px;
            }
            .btn-primary {
                background: linear-gradient(135deg, var(--primary-main), var(--primary-light));
                color: white;
                box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2);
            }
            .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 6px 16px rgba(0, 123, 255, 0.3); }

            .main-content {
                display: flex;
                gap: 25px;
                flex: 1;
                min-height: 0; /* Essencial para o layout flex funcionar corretamente */
            }
            
            .sidebar {
                width: 320px;
                flex-shrink: 0;
                background: var(--surface-alpha);
                backdrop-filter: blur(8px);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
                border: 1px solid var(--border-color);
                display: flex;
                flex-direction: column;
            }
            .sidebar h3 {
                font-weight: 600;
                font-size: 18px;
                padding-bottom: 8px;
                margin-bottom: 16px;
                border-bottom: 1px solid var(--border-color);
            }
            
            .btn-new-chat {
                width: 100%;
                margin-bottom: 16px;
                background: var(--surface-color);
                color: var(--primary-main);
                border: 1px solid var(--primary-main);
            }
            .btn-new-chat:hover { background: #F0F8FF; }

            .chat-list { display: flex; flex-direction: column; gap: 8px; overflow-y: auto; flex: 1;}
            .chat-list-item {
                position: relative;
                background: #fff;
                color: var(--text-light);
                border: 1px solid transparent;
                padding: 10px 14px;
                border-radius: 8px;
                width: 100%;
                text-align: left;
            }
            .chat-list-item:hover { background: #F0F8FF; }
            .chat-list-item.active {
                border-color: var(--primary-main);
                background: #E7F3FF;
                color: var(--text-dark);
                font-weight: 600;
            }
            .chat-list-item strong { display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 25px; }
            
            .edit-title-btn {
                position: absolute; right: 8px; top: 50%; transform: translateY(-50%);
                cursor: pointer; display: none; padding: 4px; color: var(--text-light);
                border-radius: 50%;
                line-height: 1;
            }
            .edit-title-btn:hover { background-color: var(--border-color); }
            .chat-list-item:hover .edit-title-btn, .chat-list-item.active .edit-title-btn { display: block; }

            .chat-container {
                flex: 1;
                display: flex;
                flex-direction: column;
                background: var(--surface-color);
                border-radius: 16px;
                box-shadow: 0 4px 24px rgba(0, 0, 0, 0.06);
                border: 1px solid var(--border-color);
                overflow: hidden; /* Garante que os filhos não ultrapassem a borda arredondada */
            }

            #chat {
                flex: 1; /* Ocupa todo o espaço vertical disponível */
                padding: 24px;
                overflow-y: auto; /* A mágica acontece aqui: scroll apenas nesta div */
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            /* Estilo da barra de scroll */
            #chat::-webkit-scrollbar, .chat-list::-webkit-scrollbar { width: 6px; }
            #chat::-webkit-scrollbar-track, .chat-list::-webkit-scrollbar-track { background: transparent; }
            #chat::-webkit-scrollbar-thumb, .chat-list::-webkit-scrollbar-thumb { background: var(--border-color); border-radius: 3px; }
            #chat::-webkit-scrollbar-thumb:hover, .chat-list::-webkit-scrollbar-thumb:hover { background: #b0b0b0; }

            .message { max-width: 85%; padding: 12px 20px; border-radius: 18px; font-size: 15px; word-wrap: break-word; animation: slideIn 0.3s ease-out; }
            @keyframes slideIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
            
            .msg-user { background: linear-gradient(135deg, var(--primary-main), var(--primary-light)); color: white; align-self: flex-end; box-shadow: 0 4px 12px rgba(0, 123, 255, 0.2); }
            .msg-ai { background: var(--ai-msg-bg); color: var(--text-dark); align-self: flex-start; }
            
            .controls { padding: 16px 24px; background: rgba(240, 248, 255, 0.8); border-top: 1px solid var(--border-color); display: flex; gap: 12px; align-items: center; flex-shrink: 0; }
            #question { flex: 1; padding: 12px 20px; border: 1px solid var(--border-color); border-radius: 25px; font-size: 15px; background: white; transition: all 0.2s ease; }
            #question:focus { border-color: var(--primary-main); box-shadow: 0 0 0 3px rgba(0, 123, 255, 0.15); }
            .send-btn { padding: 10px 18px; border-radius: 25px; }

            .empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; color: var(--text-light); font-size: 18px; text-align: center; }
            .status-indicator { display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-left: 8px; transition: all 0.3s ease; }
            .status-connected { background: #28a745; box-shadow: 0 0 8px #28a745; }
            .status-disconnected { background: #dc3545; }

            .typing-indicator { display: none; padding: 16px 20px; background: var(--ai-msg-bg); border-radius: 18px; align-self: flex-start; }
            .typing-dots { display: flex; gap: 4px; align-items: center; }
            .typing-dots span { width: 8px; height: 8px; background: var(--text-light); border-radius: 50%; animation: bounce 1.4s infinite ease-in-out both; }
            .typing-dots span:nth-child(1) { animation-delay: -0.32s; }
            .typing-dots span:nth-child(2) { animation-delay: -0.16s; }
            @keyframes bounce { 0%, 80%, 100% { transform: scale(0); } 40% { transform: scale(1); } }

            .message p:last-child { margin-bottom: 0; }
            .message pre { background-color: #e2e8f0; padding: 16px; border-radius: 8px; margin: 1em 0; overflow-x: auto; font-size: 0.9em;}
            .message code { background-color: #e2e8f0; padding: 2px 5px; border-radius: 4px; font-size: 0.9em;}
            .message pre code { background-color: transparent; padding: 0; }
            .msg-user code, .msg-user pre { background-color: rgba(255,255,255,0.2); }

            footer { text-align: center; padding: 5px 20px; color: var(--text-light); font-size: 14px; flex-shrink: 0;}

            @media (max-width: 992px) {
                .sidebar { width: 250px; }
            }
            @media (max-width: 768px) {
                .container { padding: 10px; gap: 10px; width: 100%; /* Ocupa toda a largura em telas pequenas */ }
                .main-content { flex-direction: column; }
                .sidebar { width: 100%; max-height: 35vh; padding: 16px; }
                .header h2 { font-size: 22px; }
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
                    <button class="btn btn-new-chat" onclick="startNewChat()">✨ Novo Chat</button>
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
                if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); sendMessage(); }
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
                            const titleText = chat.title || 'Novo Chat';
                            btn.innerHTML = `<strong>${titleText}</strong><span class="edit-title-btn" onclick="editChatTitle(event, '${chat.chat_id}', '${titleText.replace(/'/g, "\\'")}')">✏️</span>`;
                            btn.onclick = () => openChat(chat.chat_id);
                            chatListContainer.appendChild(btn);
                        });
                        if(currentChatId) {
                            const activeBtn = document.querySelector(`.chat-list-item[data-chat-id="${currentChatId}"]`);
                            if(activeBtn) activeBtn.classList.add('active');
                        }
                    } else {
                        chatListContainer.innerHTML = "<div style='color: var(--text-light); text-align: center; padding: 20px;'>Nenhum chat encontrado</div>";
                    }
                } catch (error) { console.error("Erro ao atualizar lista de chats:", error); }
            }
            
            async function loadChats() {
                userId = document.getElementById("userId").value;
                if (!userId) { alert("Por favor, insira um User ID."); return; }
                document.getElementById("chats").innerHTML = "<p>Carregando...</p>";
                await refreshChatList();
                connectWS();
                startNewChat();
            }

            async function openChat(chatId) {
                currentChatId = chatId;
                currentSessionId = null;
                document.querySelectorAll('.chat-list-item').forEach(btn => { btn.classList.toggle('active', btn.dataset.chatId === chatId); });
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
                        // Foca na última mensagem ao abrir o chat
                        chatBox.lastElementChild?.scrollIntoView({ behavior: 'auto', block: 'end' });
                    } else { chatBox.innerHTML = '<div class="empty-state">Este chat ainda não possui mensagens.</div>'; }
                } catch (error) {
                    console.error("Erro ao abrir chat:", error);
                    chatBox.innerHTML = '<div class="empty-state" style="color: #f56565;">Erro ao carregar mensagens.</div>';
                }
            }
            
            async function editChatTitle(event, chatId, currentTitle) {
                event.stopPropagation();
                const newTitle = prompt("Digite o novo título para o chat:", currentTitle);

                if (newTitle && newTitle.trim() !== "" && newTitle !== currentTitle) {
                    try {
                        const response = await fetch(`/api/chats/${userId}/${chatId}/title`, {
                            method: 'PATCH',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ title: newTitle.trim() }),
                        });
                        if (!response.ok) { throw new Error('Falha ao atualizar o título na API.'); }
                        
                        // Recarrega a lista para refletir a nova ordem
                        await refreshChatList();
                    } catch (error) {
                        console.error("Erro ao editar título:", error);
                        alert("Não foi possível atualizar o título.");
                    }
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
                        typingIndicator.scrollIntoView({ behavior: 'smooth', block: 'end' });
                    } else if (data.type === "token") {
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
                        // Foco automático na mensagem sendo recebida
                        lastMsg.scrollIntoView({ behavior: 'auto', block: 'end' });
                    } else if (data.type === "end") {
                        typingIndicator.style.display = "none";
                        // Se o chat não existia na lista, atualiza a lista
                        if (!document.querySelector(`.chat-list-item[data-chat-id="${currentChatId}"]`)) {
                             refreshChatList();
                        }
                    } else if (data.type === "error") {
                        typingIndicator.style.display = "none";
                        alert("Erro: " + data.message);
                    }
                };
            }

            function sendMessage() {
                const qInput = document.getElementById("question");
                const q = qInput.value.trim();
                if (!q) return;
                if (!ws || ws.readyState !== WebSocket.OPEN) { alert("WebSocket não está conectado! Tentando reconectar..."); connectWS(); return; }
                const payload = { user_id: userId, question: q, chat_id: currentChatId, session_id: currentSessionId };
                ws.send(JSON.stringify(payload));
                
                const chatBox = document.getElementById("chat");
                if (chatBox.querySelector('.empty-state')) chatBox.innerHTML = "";
                
                const div = document.createElement("div");
                div.className = "message msg-user";
                div.innerHTML = marked.parse(q);
                chatBox.appendChild(div);
                
                // Foco automático na mensagem enviada
                div.scrollIntoView({ behavior: 'smooth', block: 'end' });
                
                qInput.value = "";
                qInput.focus();
            }
            window.onload = () => { loadChats(); };
        </script>
    </body>
    </html>
    """