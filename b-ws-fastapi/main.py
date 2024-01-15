import asyncio
import subprocess

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


app = FastAPI()

html = """
<!DOCTYPE html>
<html>
    <head>
        <title>WebSocket FastAPI: Echo+Ping</title>
    </head>
    <body>
        <h1>WebSocket FastAPI: Echo + Ping</h1>
        
        <p>
          Send some text and it will be echo'd back by the server.<br>
          Send the text <code>PING</code> to run a ping command on the server.<br>
          Send the text <code>CLOSE</code> to close the WebSocket.
        </p>        
        
        <form action="" onsubmit="sendWsData(event)">
            <input type="text" id="messageText" autocomplete="off"/>
            <button>Send</button>
        </form>
        <div style="background-color: black; color: greenyellow;">
            <ul id="messages" style="list-style-type: none; font-family: monospace; padding: 1em"></ul>
        </div>
        
        <script>
            const ws = new WebSocket("ws://localhost:8000/ws");

            ws.onopen = () => {
                // ws.send("Message to send");
                appendText("[Websocket open]", "color:gray;");
            };

            ws.onclose = () => {
                appendText("[Websocket closed]", "color:gray;");
            };

            ws.onmessage = (event) => {
                const data = event.data;
                console.log(data);
                appendText(data);
            };

            const sendWsData = (event) => {
                event.preventDefault();
                const input = document.getElementById("messageText");
                ws.send(input.value);
                input.value = "";
            }

            const appendText = (text, style) => {
                const ul = document.getElementById("messages");
                const li = document.createElement("li");
                if (style) {
                    li.setAttribute("style", style);
                }
                const content = document.createTextNode(text);
                li.appendChild(content);
                ul.appendChild(li);
            }
        </script>
    </body>
</html>
"""


@app.get("/")
async def get():
    return HTMLResponse(html)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            if data == "PING":
                with subprocess.Popen(["ping", "8.8.8.8", "-i", "2", "-c", "10"],
                                      stdout=subprocess.PIPE,
                                      bufsize=1,
                                      universal_newlines=True) as process:
                    for line in process.stdout:
                        line = line.rstrip()
                        print(line)
                        await websocket.send_text(line)
            elif data == "CLOSE":
                break
            else:
                await websocket.send_text(f"Echo: {data}")
            # Not sure if we really need to sleep (it was not in the original code).
            await asyncio.sleep(.5)
        await websocket.close()
    except WebSocketDisconnect as exc:
        print("WebSocket closed by client")

