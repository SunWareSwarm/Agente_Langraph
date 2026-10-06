from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from config import Settings
from tools import TOOLS

SYSTEM_PROMPT = """Sos un asistente de atención a clientes que consulta una base de datos de pedidos.
Reglas:
- Usá las herramientas disponibles cuando necesites datos concretos. No inventes cifras.
- Si una herramienta devuelve un campo 'error', intentá de nuevo con otros parámetros si tiene sentido,
  o pedile una aclaración al usuario.
- Cuando tengas la información suficiente, respondé en español, de forma breve y clara."""


def build_graph(settings: Settings, checkpointer: BaseCheckpointSaver):
    llm = ChatGoogleGenerativeAI(
        model=settings.model_name,
        google_api_key=settings.google_api_key,
        temperature=0,
    )
    model_with_tools = llm.bind_tools(TOOLS)

    async def call_model(state: MessagesState) -> dict:
        messages = [SystemMessage(content=SYSTEM_PROMPT), *state["messages"]]
        response = await model_with_tools.ainvoke(messages)
        return {"messages": [response]}

    builder = StateGraph(MessagesState)
    builder.add_node("agent", call_model)
    builder.add_node("tools", ToolNode(TOOLS))

    builder.add_edge(START, "agent")
    builder.add_conditional_edges("agent", tools_condition)
    builder.add_edge("tools", "agent")

    return builder.compile(checkpointer=checkpointer)