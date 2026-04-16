# 🧠 Minha Vida — Assistente Pessoal Inteligente

Plataforma pessoal com IA para organizar tarefas, notas, finanças e ideias.

## Funcionalidades

- **✅ Tarefas** — crie, priorize e conclua tarefas por categoria
- **📝 Notas** — anote ideias, estudos, trabalho e mais
- **💰 Finanças** — controle receitas e despesas com saldo em tempo real
- **🤖 Assistente IA** — converse em português e peça para criar qualquer coisa

## Instalação rápida

### 1. Configure a chave da IA
```bash
cp backend/.env.example backend/.env
# Edite backend/.env e coloque sua ANTHROPIC_API_KEY
```

### 2. Inicie o servidor
```bash
chmod +x start.sh
./start.sh
```

### 3. Acesse
Abra [http://localhost:8000](http://localhost:8000) no navegador.

## Como usar a IA

Na aba **Assistente IA**, você pode falar naturalmente:

- *"Cria uma tarefa: estudar Python amanhã, prioridade alta"*
- *"Anota uma ideia: criar um app de receitas"*
- *"Adiciona R$ 5000 de salário hoje"*
- *"Quais são minhas tarefas urgentes?"*
- *"Me dá um resumo das minhas finanças"*
- *"Marca a tarefa 3 como concluída"*

## Estrutura

```
privacy/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI app
│   │   ├── models.py        # Modelos do banco
│   │   ├── schemas.py       # Validação Pydantic
│   │   ├── database.py      # SQLite
│   │   └── routers/
│   │       ├── tasks.py
│   │       ├── notes.py
│   │       ├── finance.py
│   │       └── ai_chat.py   # IA com tool use
│   └── requirements.txt
├── frontend/
│   └── index.html           # SPA com Alpine.js + Tailwind
└── start.sh
```

## Stack

- **Backend**: Python + FastAPI + SQLite
- **IA**: Claude Sonnet (Anthropic) com tool use
- **Frontend**: HTML + Alpine.js + Tailwind CSS (sem build)
