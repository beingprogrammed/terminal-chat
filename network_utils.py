import asyncio
import websockets
import json
import base64
import os
from crypto_utils import CryptoManager

class Peer:
    def __init__(self, host='0.0.0.0', port=8765, crypto_manager=None):
        self.host = host
        self.port = port
        self.crypto_manager = crypto_manager
        self.connection = None
        self.on_message_callback = None
        self.connection_event = asyncio.Event()
        self.is_relay = False
        self.room_id = None

    def set_on_message(self, callback):
        self.on_message_callback = callback

    async def start_server(self):
        """Starts a local P2P server."""
        self.is_relay = False
        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()  # run forever

    async def connect_to_peer(self, peer_ip):
        """Connects directly to a peer IP (Local P2P)."""
        self.is_relay = False
        uri = f"ws://{peer_ip}:{self.port}"
        self.connection = await websockets.connect(uri)
        self.connection_event.set()
        asyncio.create_task(self.listen(self.connection))

    async def connect_to_relay(self, relay_url, room_id):
        """Connects to a global relay server."""
        self.is_relay = True
        self.room_id = room_id
        self.connection = await websockets.connect(relay_url)
        # Register the room
        await self.connection.send(json.dumps({
            "type": "register",
            "room_id": room_id
        }))
        self.connection_event.set()
        asyncio.create_task(self.listen(self.connection))

    async def handle_connection(self, websocket):
        self.connection = websocket
        self.connection_event.set()
        await self.listen(websocket)

    async def listen(self, websocket):
        try:
            async for message in websocket:
                data = json.loads(message)
                
                # If it's a relay error
                if data.get('type') == 'error':
                    if self.on_message_callback:
                        await self.on_message_callback({"type": "text", "content": f"[bold red]Relay Error:[/] {data.get('message')}"})
                    continue

                if self.crypto_manager:
                    try:
                        if data['type'] == 'text':
                            data['content'] = self.crypto_manager.decrypt_str(data['content'].encode())
                        elif data['type'] == 'file':
                            # Decrypt binary data
                            encrypted_content = base64.b64decode(data['content'])
                            data['content'] = self.crypto_manager.decrypt(encrypted_content)
                    except Exception as e:
                        if data['type'] == 'text':
                            data['content'] = f"[bold red]Decryption Failed:[/] (Check keys)"
                        elif data['type'] == 'file':
                            data['content'] = b"Decryption Failed"
                
                if self.on_message_callback:
                    await self.on_message_callback(data)
        except websockets.exceptions.ConnectionClosed:
            self.connection_event.clear()
            self.connection = None
            if self.on_message_callback:
                await self.on_message_callback({"type": "text", "content": "[bold red]System:[/] Connection closed."})

    async def send_text(self, text):
        if self.connection:
            content = text
            if self.crypto_manager:
                content = self.crypto_manager.encrypt(text).decode()
            
            message = json.dumps({"type": "text", "content": content})
            await self.connection.send(message)

    async def send_file(self, file_path):
        if self.connection and os.path.exists(file_path):
            filename = os.path.basename(file_path)
            with open(file_path, "rb") as f:
                content = f.read()
            
            if self.crypto_manager:
                # Encrypt binary content
                encrypted_content = self.crypto_manager.encrypt(content)
                content_to_send = base64.b64encode(encrypted_content).decode()
            else:
                content_to_send = base64.b64encode(content).decode()

            message = json.dumps({
                "type": "file",
                "filename": filename,
                "content": content_to_send
            })
            await self.connection.send(message)

    async def send_media(self, media_type, content):
        if self.connection:
            # Media (Audio/Video) is sent unencrypted for performance by default in this app
            # but can be added if needed.
            message = json.dumps({
                "type": "media",
                "media_type": media_type,
                "content": content
            })
            await self.connection.send(message)
