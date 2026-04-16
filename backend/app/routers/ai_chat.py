import os
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
import anthropic
from ..database import get_db
from ..models import Task, Note, Finance, ChatMessage
from ..schemas import ChatMessageCreate, ChatMessageOut

router = APIRouter(prefix="/chat", tags=["chat"])

TOOLS = [
    {
        "name": "criar_tarefa",
        "description": "Cria uma nova tarefa/compromisso para o usuário.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título da tarefa"},
                "description": {"type": "string", "description": "Descrição detalhada"},
                "priority": {"type": "string", "enum": ["low", "medium", "high"], "description": "Prioridade"},
                "category": {"type": "string", "description": "Categoria (trabalho, estudo, pessoal, etc.)"},
                "due_date": {"type": "string", "description": "Data de vencimento (YYYY-MM-DD)"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "criar_nota",
        "description": "Cria uma nova nota/anotação para o usuário.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Título da nota"},
                "content": {"type": "string", "description": "Conteúdo da nota"},
                "category": {
                    "type": "string",
                    "enum": ["geral", "ideia", "estudo", "trabalho", "pessoal"],
                    "description": "Categoria da nota",
                },
                "tags": {"type": "string", "description": "Tags separadas por vírgula"},
            },
            "required": ["title", "content"],
        },
    },
    {
        "name": "adicionar_financas",
        "description": "Adiciona um lançamento financeiro (receita ou despesa).",
        "input_schema": {
            "type": "object",
            "properties": {
                "description": {"type": "string", "description": "Descrição do lançamento"},
                "amount": {"type": "number", "description": "Valor em reais"},
                "type": {"type": "string", "enum": ["income", "expense"], "description": "Tipo: receita ou despesa"},
                "category": {"type": "string", "description": "Categoria (salário, alimentação, transporte, etc.)"},
                "date": {"type": "string", "description": "Data no formato YYYY-MM-DD"},
            },
            "required": ["description", "amount", "type", "date"],
        },
    },
    {
        "name": "marcar_tarefa_concluida",
        "description": "Marca uma tarefa como concluída pelo ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "integer", "description": "ID da tarefa a concluir"},
            },
            "required": ["task_id"],
        },
    },
]


def _build_context(db: Session) -> str:
    tasks = db.query(Task).order_by(Task.created_at.desc()).limit(30).all()
    notes = db.query(Note).order_by(Note.created_at.desc()).limit(20).all()
    income = db.query(func.sum(Finance.amount)).filter(Finance.type == "income").scalar() or 0
    expense = db.query(func.sum(Finance.amount)).filter(Finance.type == "expense").scalar() or 0
    recent_finances = db.query(Finance).order_by(Finance.date.desc()).limit(10).all()

    pending_tasks = [t for t in tasks if t.status != "done"]
    done_tasks = [t for t in tasks if t.status == "done"]

    ctx = "=== CONTEXTO DO USUÁRIO ===\n\n"

    ctx += f"TAREFAS PENDENTES ({len(pending_tasks)}):\n"
    for t in pending_tasks:
        ctx += f"  [ID:{t.id}] [{t.priority.upper()}] {t.title}"
        if t.due_date:
            ctx += f" (vence: {t.due_date})"
        if t.category:
            ctx += f" | cat: {t.category}"
        ctx += f" | status: {t.status}\n"

    ctx += f"\nTAREFAS CONCLUÍDAS ({len(done_tasks)}):\n"
    for t in done_tasks[:5]:
        ctx += f"  [ID:{t.id}] {t.title}\n"

    ctx += f"\nNOTAS RECENTES ({len(notes)}):\n"
    for n in notes:
        ctx += f"  [ID:{n.id}] [{n.category}] {n.title}"
        if n.tags:
            ctx += f" (tags: {n.tags})"
        ctx += f"\n    {n.content[:200]}{'...' if len(n.content) > 200 else ''}\n"

    ctx += f"\nFINANÇAS:\n"
    ctx += f"  Receitas totais: R$ {income:.2f}\n"
    ctx += f"  Despesas totais: R$ {expense:.2f}\n"
    ctx += f"  Saldo: R$ {income - expense:.2f}\n"
    ctx += f"\nÚLTIMOS LANÇAMENTOS:\n"
    for f in recent_finances:
        sign = "+" if f.type == "income" else "-"
        ctx += f"  {f.date} | {sign}R${f.amount:.2f} | {f.description} ({f.category})\n"

    return ctx


def _execute_tool(tool_name: str, tool_input: dict, db: Session) -> str:
    if tool_name == "criar_tarefa":
        task = Task(**{k: v for k, v in tool_input.items() if v is not None})
        db.add(task)
        db.commit()
        db.refresh(task)
        return f"Tarefa criada com sucesso! ID: {task.id}, Título: {task.title}"

    elif tool_name == "criar_nota":
        note = Note(**{k: v for k, v in tool_input.items() if v is not None})
        db.add(note)
        db.commit()
        db.refresh(note)
        return f"Nota criada com sucesso! ID: {note.id}, Título: {note.title}"

    elif tool_name == "adicionar_financas":
        entry = Finance(**tool_input)
        db.add(entry)
        db.commit()
        db.refresh(entry)
        tipo = "Receita" if entry.type == "income" else "Despesa"
        return f"{tipo} adicionada! ID: {entry.id}, Valor: R${entry.amount:.2f}"

    elif tool_name == "marcar_tarefa_concluida":
        task = db.query(Task).filter(Task.id == tool_input["task_id"]).first()
        if not task:
            return f"Tarefa ID {tool_input['task_id']} não encontrada."
        task.status = "done"
        db.commit()
        return f"Tarefa '{task.title}' marcada como concluída!"

    return "Ação desconhecida."


@router.get("/history", response_model=List[ChatMessageOut])
def get_history(limit: int = 50, db: Session = Depends(get_db)):
    return (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]
    )


@router.post("/send")
def send_message(msg: ChatMessageCreate, db: Session = Depends(get_db)):
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY não configurada")

    user_msg = ChatMessage(role="user", content=msg.content)
    db.add(user_msg)
    db.commit()

    history = (
        db.query(ChatMessage)
        .order_by(ChatMessage.created_at.desc())
        .limit(20)
        .all()[::-1]
    )

    context = _build_context(db)
    system_prompt = f"""Você é um assistente pessoal inteligente chamado **Minha Vida**.
Você ajuda o usuário a organizar sua vida: tarefas, anotações, finanças, estudos e ideias.

O usuário é uma pessoa ocupada que esquece as coisas facilmente. Sua missão é:
- Responder de forma concisa e prática (em português)
- Usar as ferramentas disponíveis para criar tarefas, notas e lançamentos financeiros quando o usuário pedir
- Dar sugestões e insights baseados nos dados do usuário
- Lembrar o usuário de tarefas urgentes e vencidas
- Ajudar a priorizar o que é mais importante

Quando o usuário pedir para adicionar algo, USE as ferramentas imediatamente.
Responda sempre em português do Brasil.

{context}"""

    messages = [{"role": m.role, "content": m.content} for m in history[:-1]]
    messages.append({"role": "user", "content": msg.content})

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        tools=TOOLS,
        messages=messages,
    )

    tool_results = []
    assistant_text = ""

    if response.stop_reason == "tool_use":
        tool_calls_content = response.content
        tool_results_content = []

        for block in response.content:
            if block.type == "tool_use":
                result = _execute_tool(block.name, block.input, db)
                tool_results_content.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })
                tool_results.append(result)

        messages.append({"role": "assistant", "content": tool_calls_content})
        messages.append({"role": "user", "content": tool_results_content})

        follow_up = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOLS,
            messages=messages,
        )
        for block in follow_up.content:
            if hasattr(block, "text"):
                assistant_text += block.text
    else:
        for block in response.content:
            if hasattr(block, "text"):
                assistant_text += block.text

    full_response = assistant_text
    if tool_results:
        full_response = assistant_text

    ai_msg = ChatMessage(role="assistant", content=full_response)
    db.add(ai_msg)
    db.commit()
    db.refresh(ai_msg)

    return {
        "id": ai_msg.id,
        "role": "assistant",
        "content": full_response,
        "tool_results": tool_results,
        "created_at": ai_msg.created_at,
    }


@router.delete("/history")
def clear_history(db: Session = Depends(get_db)):
    db.query(ChatMessage).delete()
    db.commit()
    return {"ok": True}
