Saturday 2024.01.13 11:16:29

**WebSocket Demos**
===================

Docs:
 - WebSockets with FastAPI: https://fastapi.tiangolo.com/advanced/websockets/
 - Local storage in browser: https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage


Extra stuff, not related to WebSockets:
 - Drag and drop files: https://github.com/puntonim/drag-drop-file-upload-demos/
 - Pipe 2 processes in Popen: https://www.datacamp.com/tutorial/python-subprocess
 - Ngrok with 2 tunnels:
   File: `~/.config/ngrok/ngrok.yml`
   ```yml
       authtoken: ...
       log: ngrok.log
       tunnels:
         first:
           addr: 3000
           proto: http
           bind_tls: true
         second:
           addr: 8000
           proto: http
           bind_tls: true
   ```
   Run: `$ ngrok start --all`
