```markdown
# Chat With Stream (FastAPI + LangChain + AWS Bedrock)

Este projeto é uma API **FastAPI** que expõe um **WebSocket** para chat em **streaming** com modelos do **AWS Bedrock** via **LangChain**.  
A resposta do modelo é enviada **token a token em tempo real** para o cliente conectado.

---

## 🚀 Tecnologias

- [FastAPI](https://fastapi.tiangolo.com/) — Web framework assíncrono.
- [LangChain](https://www.langchain.com/) — Orquestração de LLMs.
- [AWS Bedrock](https://aws.amazon.com/bedrock/) — Modelos de linguagem gerenciados.
- [Dependency Injector](https://python-dependency-injector.ets-labs.org/) — Injeção de dependência.
- WebSocket — Canal de comunicação bidirecional em tempo real.
- Docker — Containerização da aplicação.

---

## 📂 Estrutura do Projeto

```

.
├── app
│   ├── adapter
│   │   ├── routers           # Rotas WebSocket
│   │   └── schemas           # Schemas Pydantic
│   ├── core
│   │   ├── config.py         # Configurações da aplicação
│   │   ├── exceptions.py     # Exceções customizadas
│   │   └── service
│   │       ├── chat          # ChatService (fachada)
│   │       └── llm           # Serviços LangChain/Bedrock
│   ├── container.py          # Container de dependências
├── main.py                   # EntryPoint FastAPI/Uvicorn
├── requirements.txt
├── Dockerfile
├── .gitignore
├── .dockerignore
└── README.md

````

---

## ⚙️ Configuração

Crie um arquivo `.env` com suas credenciais AWS:

```env
AWS_PROFILE=default
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-micro-v1:0
TEMPERATURE=0.3
PORT=8000
````

---

## ▶️ Rodando localmente

### 1. Ambiente virtual

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Executar servidor

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

---

## 🐳 Rodando com Docker

```bash
docker build -t chat-with-stream .
docker run -it --rm -p 8000:8000 --env-file .env chat-with-stream
```

---

## 💬 Uso via WebSocket

### URL

```
ws://localhost:8000/ws/chat/completions
```

### Mensagem inicial (JSON)

```json
{
  "question": "Explique resumidamente o que é LangChain.",
  "session_id": "sessao-teste-1"
}
```

### Resposta esperada

```json
{"type":"start","session_id":"sessao-teste-1"}
{"type":"token","text":"LangChain"}
{"type":"token","text":" é um framework..."}
{"type":"end","full_text":"LangChain é um framework..."}
```

### Encerramento automático

* Se o cliente fechar o WebSocket (reload/aba fechada), o backend encerra a sessão.
