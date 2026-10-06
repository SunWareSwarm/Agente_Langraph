# Agente de razonamiento cíclico con memoria persistente

Agente conversacional construido con **LangGraph** y **Gemini** que decide por sí mismo cuándo llamar a herramientas, reintenta o pide aclaraciones ante errores, y recuerda interacciones previas dentro de una misma sesión usando un `thread_id`.

El caso de uso es la consulta de una base de datos ficticia de pedidos de clientes.

## Características

- **Autonomía:** el LLM decide qué herramienta usar según el prompt del usuario, sin rutas `if/else` manuales. La lógica de enrutamiento está en un `StateGraph` con `tools_condition`.
- **Ciclo de retorno:** si una herramienta devuelve un error, el agente puede volver a intentar con otros parámetros o pedir una aclaración al usuario.
- **Resiliencia de estado:** con el mismo `thread_id`, el agente recuerda el contexto de la conversación. Persistencia con SQLite.
- **Límite de recursión:** el grafo tiene un techo de pasos (`recursion_limit`) para evitar bucles infinitos y costos inesperados.
- **Asíncrono:** todo el flujo usa `asyncio`, `ainvoke` y `AsyncSqliteSaver`.

## Stack

- Python 3.12
- LangGraph
- LangChain Core y `langchain-google-genai`
- Modelo: `gemini-3.5-flash` (configurable)
- SQLite para persistencia (`langgraph-checkpoint-sqlite`)

## Estructura del proyecto

```
.
├── config.py          # Carga de configuración desde variables de entorno
├── tools.py           # Herramientas (@tool) sobre una base de datos ficticia
├── graph.py           # StateGraph: nodo del modelo, nodo de herramientas y aristas
├── main.py            # Ejecución de prueba multi-paso y generación de la traza
├── requirements.txt
├── .env.example
├── .gitignore
└── traces/
    └── traza_ejecucion.json   # Traza del ciclo ReAct
```

## Requisitos previos

- Python 3.12 (no funciona con versiones anteriores ni con 3.13+ sin verificar compatibilidad)
- Una API key de Google AI Studio: https://aistudio.google.com/apikey

## Instalación y ejecución

**1. Clonar el repositorio**


**2. Crear y activar el entorno virtual**

macOS / Linux:
```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Configurar las variables de entorno**

Copiá el archivo de ejemplo y completá tu API key:
```bash
cp .env.example .env
```

En Windows: `copy .env.example .env`

Contenido de `.env`:
```env
GOOGLE_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-3.5-flash
SQLITE_PATH=checkpoints.db
RECURSION_LIMIT=10
```

El archivo `.env` está en `.gitignore` y nunca debe subirse al repositorio.

**5. Ejecutar la prueba**
```bash
python main.py
```

Esto ejecuta una conversación de varios turnos con el mismo `thread_id`, genera `traces/traza_ejecucion.json` y guarda el estado de la sesión en `checkpoints.db`.

## Traza de ejecución

La traza en `traces/traza_ejecucion.json` muestra el ciclo ReAct completo:

1. El usuario pregunta cuántos pedidos tuvo el cliente 102 y cuál fue el total.
2. El agente decide llamar a `buscar_pedidos` con `cliente_id: 102`.
3. La herramienta devuelve `{"pedidos": 3, "total": 14500}`.
4. El agente razona que ya tiene los datos y responde.
5. En el siguiente turno, con el mismo `thread_id`, el usuario pregunta "¿y el último?". El agente recuerda el cliente y llama a `obtener_ultimo_pedido`.
6. Si se consulta un cliente inexistente, la herramienta devuelve un error y el agente informa la situación.

## Cómo funciona

```
START → agent ──(tool_calls?)──► tools ──► agent
                  │
                  └── no ──► END
```

- **agent:** llama al modelo Gemini con las herramientas vinculadas (`bind_tools`) y un system prompt que define el comportamiento ante errores.
- **tools:** ejecuta la herramienta solicitada con `ToolNode` y devuelve el resultado al estado.
- **tools_condition:** decide si hay que volver a las herramientas o terminar.
- **Checkpointer:** `AsyncSqliteSaver` guarda el estado de cada `thread_id`, lo que permite continuar conversaciones.

## Notas

- La consigna pide `SqliteSaver`; se usa `AsyncSqliteSaver` (`langgraph.checkpoint.sqlite.aio`) porque la ejecución es asíncrona.
- Los datos de pedidos son ficticios y están en memoria dentro de `tools.py`.