from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List
from controller import *
import json

app = FastAPI()

origins = ["http://127.0.0.1:5500"]  # Adjust as per your CORS needs

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
#Nombre, Edad, Sexo, Número de Cédula, Teléfono, Email
def extraer_nombre(nombre):
    """Extrae el nombre y lo coloca en el formato json estandar"""
    return json.dumps({"nombre": nombre})

def extraer_edad(edad):
    """Extrae la edad y la coloca en el formato json estandar"""
    return json.dumps({"edad": edad})

def extraer_sexo(sexo):
    """Extrae el sexo y lo coloca en el formato json estandar"""
    return json.dumps({"sexo": sexo})

def extraer_cedula(cedula):
    """Extrae el número de cédula de identidad y lo coloca en el formato json estandar"""
    return json.dumps({"cedula": cedula})

def extraer_telefono(telefono):
    """Extrae el número de teléfono y lo coloca en el formato json estandar"""
    return json.dumps({"teléfono": telefono})

def extraer_email(email):
    """Extrae el email y lo coloca en el formato json estandar"""
    return json.dumps({"email": email})
    
function_list = {
            "extraer_nombre": extraer_nombre,
            "extraer_edad": extraer_edad,
            "extraer_sexo": extraer_sexo,
            "extraer_cedula": extraer_cedula,
            "extraer_telefono": extraer_telefono,
            "extraer_email": extraer_email
        }

lista_de_tools = [
    {
        "type": "function",
        "function": {
            "name": "extraer_nombre",
            "description": "Extrae el nombre una persona de un texto dado, identificando y seleccionando únicamente caracteres que conformen nombres propios en español. Utiliza patrones y heurísticas para distinguir nombres dentro del texto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "nombre": {
                        "type": "string",
                        "description": "Texto que contiene el nombre de una persona, identificado por patrones comunes en nombres propios en español."
                    }
                },
                "required": ["nombre"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extraer_edad",
            "description": "Identifica y extrae la edad de una persona en años de un texto, utilizando patrones numéricos y contextos que indiquen claramente la edad.",
            "parameters": {
                "type": "object",
                "properties": {
                    "edad": {
                        "type": "number",
                        "description": "La edad de una persona expresada en años, identificada mediante patrones numéricos y contextos específicos."
                    }
                },
                "required": ["edad"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extraer_sexo",
            "description": "Determina el sexo de una persona basándose en indicadores textuales específicos, diferenciando entre masculino y femenino.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sexo": {
                        "type": "string",
                        "description": "El sexo de la persona, determinado a partir de indicadores textuales, con solo dos valores posibles: 'masculino' o 'femenino'."
                    }
                },
                "required": ["sexo"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extraer_cedula",
            "description": "Extrae y valida el número de cédula de identidad ecuatoriana de un texto, asegurándose de que tenga 10 dígitos y que los dos primeros dígitos correspondan a un código de provincia válido (01-24).",
            "parameters": {
                "type": "object",
                "properties": {
                    "cedula": {
                        "type": "string",
                        "description": "Número de cédula de identidad ecuatoriana, validado por tener exactamente 10 dígitos y que inicie con un código de provincia entre 01 y 24."
                    }
                },
                "required": ["cedula"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extraer_telefono",
            "description": "Detecta y extrae números de teléfono ecuatorianos de un texto, validando que tengan 10 dígitos y comiencen con '09', indicativo de números de celular en Ecuador.",
            "parameters": {
                "type": "object",
                "properties": {
                    "telefono": {
                        "type": "string",
                        "description": "Número de teléfono celular ecuatoriano, validado por tener exactamente 10 dígitos y comenzar con '09'."
                    }
                },
                "required": ["telefono"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "extraer_email",
            "description": "Identifica y extrae direcciones de correo electrónico de un texto, reconociendo distintos dominios y formatos comunes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "email": {
                        "type": "string",
                        "description": "Dirección de correo electrónico identificada dentro de un texto, cubriendo diversos dominios y formatos de email."
                    }
                },
                "required": ["email"]
            }
        }
    }
]

datos = {}
datosPrevios = {}
llamados = 0
def run_conversation(lista_de_mensajes, herramientas = lista_de_tools, available_functions=function_list):
    global llamados
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
    datosPrevios = datos.copy()

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
            datos.update(json.loads(function_response))
            print(json.dumps(datos))
            
            if (datos != datosPrevios):
                llamados += 1
                print(llamados)
            if (llamados == 6):
                registrarEntrada(datos_cliente=datos)
            
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
        return second_response.choices[0].message.content #+ " acabo de anotar tu " + primer_parametro +  " en una variable: " + function_response
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