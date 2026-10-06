import asyncio
import json
from pathlib import Path

from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from config import load_settings
from graph import build_graph

TRACE_PATH = Path("traces/traza_ejecucion.json")


def serialize(msg: BaseMessage) -> dict:
    data = {"tipo": msg.type, "contenido": msg.content}
    if getattr(msg, "tool_calls", None):
        data["tool_calls"] = [{"nombre": tc["name"], "args": tc["args"]} for tc in msg.tool_calls]
    if msg.type == "tool":
        data["herramienta"] = msg.name
    return data


async def ask(graph, config: dict, pregunta: str, trace: list[dict]) -> None:
    previos = (await graph.aget_state(config)).values.get("messages", [])
    trace.append({"usuario": pregunta, "thread_id": config["configurable"]["thread_id"]})

    result = await graph.ainvoke({"messages": [HumanMessage(content=pregunta)]}, config=config)

    nuevos = result["messages"][len(previos):]
    trace.extend(serialize(m) for m in nuevos)
    print(f"\nUsuario: {pregunta}")
    print(f"Respuesta: {result['messages'][-1].content}")


async def main() -> None:
    settings = load_settings()
    trace: list[dict] = []
    config = {
        "configurable": {"thread_id": "sesion-demo-1"},
        "recursion_limit": settings.recursion_limit,
    }

    async with AsyncSqliteSaver.from_conn_string(settings.sqlite_path) as checkpointer:
        graph = build_graph(settings, checkpointer)

        await ask(graph, config, "¿Cuántos pedidos tuvo el cliente 102 y cuál fue el total?", trace)
        await ask(graph, config, "¿y el último?", trace)  # Prueba de memoria con el mismo thread_id

    TRACE_PATH.parent.mkdir(exist_ok=True)
    TRACE_PATH.write_text(json.dumps(trace, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    print(f"\nTraza guardada en {TRACE_PATH}")


if __name__ == "__main__":
    asyncio.run(main())