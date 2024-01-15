# Cookie auth inspired by: https://gist.github.com/rochacbruno/3b8dbb79b2b6c54486c396773fdde532

import asyncio
import subprocess
from pathlib import Path
from typing import Annotated

from fastapi import (
    Cookie,
    Depends,
    FastAPI,
    Form,
    HTTPException,
    Response,
    WebSocket,
    WebSocketDisconnect,
)
from fastapi.staticfiles import StaticFiles
from passlib.context import CryptContext

from session_manager import SessionManager, SessionNotFound

ROOT_DIR = Path(__file__).parent

CREDENTIALS = {
    # Use `hash_password()` to generate new passwords.
    "admin": "$2b$12$j4r7UinmMbMTcDzZbcyDR.VzSVguTxlYXymfAoFBFPU9jFRwdwQSi",
}


app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
session_mgr = SessionManager()


def _hash_password(plain: str) -> str:
    return pwd_context.hash(plain)


def _verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


@app.post("/api/login")
async def api_login(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    response: Response,
):
    hashed_password = CREDENTIALS.get(username)
    if not hashed_password or not _verify_password(password, hashed_password):
        raise HTTPException(status_code=401)

    sessionid = session_mgr.create_new_session(username)
    response.set_cookie(key="sessionid", value=sessionid)


@app.post("/api/logout")
async def api_logout(
    response: Response, sessionid: Annotated[str | None, Cookie()] = None
):
    response.delete_cookie(key="sessionid")
    if sessionid:
        session_mgr.delete_session(sessionid)


async def get_auth_user(sessionid: Annotated[str | None, Cookie()] = None):
    if not sessionid:
        raise HTTPException(status_code=401)

    try:
        sessionid, username = session_mgr.get_session(sessionid)
    except SessionNotFound as exc:
        raise HTTPException(status_code=403)

    return username


@app.get("/api/me")
async def api_me(username: Annotated[str, Depends(get_auth_user)]):
    return username


@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    sessionid: Annotated[str | None, Cookie()] = None,
):
    await websocket.accept()

    # Accept the websocket first, even before sending an auth error.
    # That is because if we do not accept (reject) the websocket connection then
    #  the client cannot read any header nor status code in the reject response. So
    #  the client cannot understand why the websocket was rejected (by security design).
    # See:https://stackoverflow.com/a/50685387/1969672
    try:
        await get_auth_user(sessionid)
    except HTTPException as exc:
        # Websocket status codes: https://developer.mozilla.org/en-US/docs/Web/API/CloseEvent/code.
        return await websocket.close(1011, "forbidden")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received: {data}")
            if data == "PING":
                with subprocess.Popen(
                    ["ping", "8.8.8.8", "-i", "2", "-c", "10"],
                    stdout=subprocess.PIPE,
                    bufsize=1,
                    universal_newlines=True,
                ) as process:
                    for line in process.stdout:
                        line = line.rstrip()
                        print(line)
                        await websocket.send_text(line)
            elif data == "CLOSE":
                break
            else:
                await websocket.send_text(f"Echo: {data}")
            # Not sure if we really need to sleep (it was not in the original code).
            await asyncio.sleep(0.5)
        await websocket.close()
    except WebSocketDisconnect as exc:
        print("WebSocket closed by client")


# This mount should come after all other routes defined here.
app.mount("/", StaticFiles(directory="static", html=True), name="static")
