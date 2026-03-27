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

    def set_on_message(self, callback):
        self.on_message_callback = callback

    async def start_server(self):
        async with websockets.serve(self.handle_connection, self.host, self.port):
            await asyncio.Future()  # run forever

    async def connect_to_peer(self, peer_ip):
        uri = f"ws://{peer_ip}:{self.port}"
        self.connection = await websockets.connect(uri)
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
                            data['content'] = f"[bold red]Decryption Failed:[/] (Check if both peers used the same secret number)"
                        else:
                            data['content'] = b"Decryption Failed"
                
                if self.on_message_callback:
                    await self.on_message_callback(data)
        except websockets.exceptions.ConnectionClosed:
            self.connection_event.clear()
            self.connection = None
            print("\nConnection closed.")

    async def send_text(self, text):
        if self.connection:
            content = text
            if self.crypto_manager:
                content = self.crypto_manager.encrypt(text).decode()
            
            message = json.dumps({"type": "text", "content": content})
            await self.connection.send(message)

    async def send_media(self, media_type, content):
        if self.connection:
            # We don't encrypt media packets for performance (optional)
            message = json.dumps({
                "type": "media",
                "media_type": media_type,
                "content": content
            })
            await self.connection.send(message)
