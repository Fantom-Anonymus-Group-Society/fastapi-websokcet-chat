from fastapi import FastAPI
from app.core.base_meta import database
from app.controllers import (
    authentication_controller,
    chats_controller,
    messages_controller,
    users_controller
)
from fastapi.middleware.cors import CORSMiddleware

app: FastAPI = FastAPI(title="FastApi app")

origins: list = [
    "http://localhost",
    "http://localhost:8008",
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API controllers
app.include_router(authentication_controller.router)
app.include_router(chats_controller.router)
app.include_router(messages_controller.router)
app.include_router(users_controller.router)


@app.get('/')
async def root():
    from app.fakers.initial_seed import create_initail_state
    await create_initail_state()
    return {'detail': 'Root'}


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()
