Para correr la app instalar todas las dependencias usadas es decir hacer pip install con todos estos

from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel
from openai import OpenAI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader
from typing import List
import json

luego en la linea de comandos ejecutar: uvicorn api_nombre:app --reload

ejecutar la interfaz con live server (index.html) y debe correr perfectamente

Para crear la base de datos, verificar que en conexionBD.py este la contraseña a tu mysql y luego ejecuta en una query tabla_data.sql