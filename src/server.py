import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.connection_manager import ConnectionManager
from src.database import get_user
from src.user import User
from src.models.user import UserModel


app = FastAPI()
connection_manager = ConnectionManager()


@app.post('/register')
async def register(new_user: UserModel):
    user = User(new_user.username, new_user.password)

    existing_users = get_user(new_user.username)
    if existing_users is not None:
        login_response = f'Username {new_user.username} already exists, choose nother one. \n'
    else:
        user.save_user()
        login_response = 'User saved correctly'

    return JSONResponse(content=login_response)


@app.post('/login')
async def login(loged_user: UserModel):
    user = User(loged_user.username, loged_user.password)
    if user.find_user() and user.check_password(loged_user.password):
        return RedirectResponse('/chat', status_code=200)

    return JSONResponse(content='Username or password incorrect.', status_code=401)


@app.websocket('/chat')
async def websocket_endpoint(websocket: WebSocket):
    await connection_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f'Received: {data}')
            await connection_manager.broadcast(websocket, data)

    except WebSocketDisconnect:
        # Remove the connection from the list of active connections
        user_id = connection_manager.disconnect(websocket)
        # Broadcast the disconnection of client with id to all the clients except the one who sent
        await connection_manager.broadcast(websocket, json.dumps({"type": "User disconnected", "id": user_id}))


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return JSONResponse(content="Not Found", status_code=404)
