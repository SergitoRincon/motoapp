import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.config import settings
from database.connection import create_tables
from routers import auth, usuarios_backend, vehiculos, mantenimiento

# Configuración de logs para ver qué pasa en Render
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s | %(levelname)s | %(message)s")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Esto crea las tablas en Supabase automáticamente al iniciar
    await create_tables()
    yield

app = FastAPI(
    title=settings.APP_NAME, 
    version=settings.APP_VERSION, 
    lifespan=lifespan
)

# Configuración de CORS: Vital para que tu App se conecte al Backend
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], # Permite conexiones desde cualquier origen (tu App)
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Registro de las rutas de tu API
app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(vehiculos.router)
app.include_router(mantenimiento.router)

@app.get("/health")
async def health():
    """Ruta para que Render sepa que el servicio está vivo"""
    return {"status": "healthy", "version": settings.APP_VERSION}