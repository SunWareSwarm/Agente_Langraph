import asyncio

from langchain_core.tools import tool

# Base de datos ficticia en memoria
_PEDIDOS: dict[int, dict[str, int]] = {
    101: {"pedidos": 2, "total": 8200},
    102: {"pedidos": 3, "total": 14500},
    103: {"pedidos": 0, "total": 0},
}

_ULTIMO_PEDIDO: dict[int, dict[str, str | int]] = {
    101: {"id": "P-7701", "fecha": "2026-08-30", "monto": 3900},
    102: {"id": "P-7781", "fecha": "2026-09-14", "monto": 4300},
}


@tool
async def buscar_pedidos(cliente_id: int) -> dict:
    """Devuelve la cantidad total de pedidos históricos y el monto total gastado
    por un cliente, a partir de su ID numérico. Usala cuando el usuario pregunte
    cuántos pedidos tuvo un cliente o cuánto gastó en total. Si el cliente no
    existe, devuelve un error con el campo 'error'."""
    await asyncio.sleep(0.1)  # Simula latencia de una base de datos real
    if cliente_id not in _PEDIDOS:
        return {"error": f"Cliente {cliente_id} no encontrado. Verificá el ID o pedí aclaración."}
    return _PEDIDOS[cliente_id]


@tool
async def obtener_ultimo_pedido(cliente_id: int) -> dict:
    """Devuelve los datos del pedido más reciente de un cliente (ID del pedido,
    fecha y monto). Usala cuando el usuario pregunte por el último pedido, la
    compra más reciente o la fecha de la última compra de un cliente."""
    await asyncio.sleep(0.1)
    if cliente_id not in _ULTIMO_PEDIDO:
        return {"error": f"No hay pedidos registrados para el cliente {cliente_id}."}
    return _ULTIMO_PEDIDO[cliente_id]


TOOLS = [buscar_pedidos, obtener_ultimo_pedido]