# Chat With Stream (FastAPI + LangChain + AWS Bedrock)

Este projeto é uma API **FastAPI** que expõe um **WebSocket** para chat em **streaming** com modelos do **AWS Bedrock** via **LangChain**.  
A resposta do modelo é enviada **token a token em tempo real** para o cliente conectado.

---

## 🚀 Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework assíncrono
- [LangChain](https://www.langchain.com/) — Orquestração de LLMs
- [AWS Bedrock](https://aws.amazon.com/bedrock/) — Modelos de linguagem gerenciados
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/) — Injeção de dependência
- WebSocket — Canal de comunicação bidirecional em tempo real
- Docker — Containerização da aplicação

---

## 📂 Estrutura do Projeto

```
.
├── app/
│   ├── adapter/
│   │   ├── routers/          # Rotas WebSocket
│   │   └── schemas/          # Schemas Pydantic
│   ├── core/
│   │   ├── config.py         # Configurações da aplicação
│   │   ├── exceptions.py     # Exceções customizadas
│   │   └── service/
│   │       ├── chat/         # ChatService (fachada)
│   │       └── llm/          # Serviços LangChain/Bedrock
│   └── container.py          # Container de dependências
├── main.py                   # EntryPoint FastAPI/Uvicorn
├── requirements.txt
├── Dockerfile
├── .gitignore
├── .dockerignore
└── README.md
```

---

## ⚙️ Configuração

Crie um arquivo `.env` na raiz do projeto com suas credenciais AWS:

```env
AWS_PROFILE=default
AWS_ACCOUNT_ID=xxxyyy
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
TEMPERATURE=0.3
PORT=8000
```

---

## ▶️ Executando Localmente

### 1. Preparar ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Executar o servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

A API estará disponível em: `http://localhost:8000`

---

## 🐳 Executando com Docker

```bash
# Build da imagem
docker build -t chat-with-stream .

# Executar container
docker run -it --rm -p 8000:8000 --env-file .env chat-with-stream
```

---

## 💬 Como Usar o WebSocket

### Endpoint
```
ws://localhost:8000/ws/chat/completions
```

### Enviando uma mensagem (JSON)
```json
{
  "question": "Explique resumidamente o que é LangChain.",
  "session_id": "sessao-teste-1"
}
```

### Formato das respostas
O servidor enviará uma sequência de mensagens JSON:

```json
{"type": "start", "session_id": "sessao-teste-1"}
{"type": "token", "text": "LangChain"}
{"type": "token", "text": " é um framework"}
{"type": "token", "text": " para desenvolvimento..."}
{"type": "end", "full_text": "LangChain é um framework para desenvolvimento..."}
```

### Tipos de resposta
- `start` — Início da resposta
- `token` — Token individual da resposta (streaming)
- `end` — Fim da resposta com texto completo
- `error` — Erro durante o processamento

### Comportamento da sessão
- Se o cliente fechar o WebSocket (reload/aba fechada), o backend encerra automaticamente a sessão
- Cada `session_id` mantém o contexto da conversa

---

## 🔧 Desenvolvimento

### Estrutura de arquitetura
- **Adapter Layer**: Rotas e schemas de entrada/saída
- **Core Layer**: Lógica de negócio e serviços
- **Service Layer**: Integração com LangChain e AWS Bedrock
- **Container**: Gerenciamento de dependências

### Principais componentes
- `ChatService`: Fachada principal para operações de chat
- `LLMService`: Integração com modelos do AWS Bedrock
- `WebSocketRouter`: Gerenciamento de conexões WebSocket

---

## 📝 Notas

- Certifique-se de ter as credenciais AWS configuradas corretamente
- O modelo padrão é o `us.anthropic.claude-3-7-sonnet-20250219-v1:0`, mas pode ser alterado no `.env`
- A temperatura padrão é `0.3` para respostas mais determinísticas
