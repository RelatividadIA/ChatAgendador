from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List
import json

app = FastAPI()

origins = ["http://127.0.0.1:5501"]  # Adjust as per your CORS needs

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

api_keys = [
    "c5435fd0-hrry-4617-krpn-9ffb829e7513",
    "ec9bcba1-tfwk-9799-rslv-378aae060441",
    "94705224-bhvg-4745-mac7-f15c455858f4"
]

api_key_header = APIKeyHeader(name='Psico-API-Key')

def get_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key in api_keys:
        return api_key
    else:
        raise HTTPException(
            status_code=HTTPException.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key"
        )

client = OpenAI()  # Use your OpenAI API key

def extraer_nombre(nombre):
    """Extrae el nombre y lo coloca en el formato json estandar"""
    return json.dumps({"nombre": nombre})

def extraer_edad(edad):
    """Extrae el nombre y lo coloca en el formato json estandar"""
    return json.dumps({"edad": edad})

function_list = {
            "extraer_nombre": extraer_nombre,
            "extraer_edad": extraer_edad
        }

lista_de_tools = [
        {
            "type": "function",
            "function": {
                "name": "extraer_nombre",
                "description": "Cuando el asistente detecta el nombre de una persona (en español), se llama a esta función para extraer el nombre de la persona y colocarlo en una variable",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nombre": {
                            "type": "string",
                            "description": "El nombre de una persona, escrito en español.",
                        },
                    },
                    "required": ["nombre"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "extraer_edad",
                "description": "Cuando el asistente detecta la edad de una persona (en años), se llama a esta función para extraer la edad de la persona (en años) y colocarlo en una variable",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "edad": {
                            "type": "number",
                            "description": "La edad de una persona en años",
                        },
                    },
                    "required": ["edad"],
                },
            },
        }
    ]


def run_conversation(lista_de_mensajes, herramientas = lista_de_tools, available_functions=function_list):
    # Step 1: send the conversation and available functions to the model
    messages = lista_de_mensajes
    tools = herramientas
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=messages,
        tools=tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # only one function in this example, but you can have multiple
        messages.append(response_message)  # extend conversation with assistant's reply
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            lista_de_parametros = list(function_args.keys())
            primer_parametro = lista_de_parametros[0]
            function_response = function_to_call(
                function_args.get(primer_parametro)
            )
            print(function_response)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        return second_response.choices[0].message.content + " acabo de anotar tu " + primer_parametro +  " en una variable: " + function_response
    return response_message.content


@app.get('/')
async def index():
    return {'message': 'API is Up and Running!'}


class ChatMessage(BaseModel):
    role: str
    content: str

class ChatInput(BaseModel):
    messages: List[ChatMessage]

@app.post("/chatgpt")
async def chat_with_gpt_extract_name(input_data: ChatInput, api_key: str = Depends(get_api_key)):
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in input_data.messages]
    return {"response": run_conversation(formatted_messages)}