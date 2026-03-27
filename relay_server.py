import asyncio
import websockets
import json

# rooms = { "room_id": [websocket1, websocket2] }
rooms = {}

async def handle_client(websocket, path=None):
    room_id = None
    try:
        # First message should be registration: {"type": "register", "room_id": "..."}
        async for message in websocket:
            data = json.loads(message)
            
            if data.get('type') == 'register':
                room_id = data.get('room_id')
                if room_id not in rooms:
                    rooms[room_id] = []
                
                if len(rooms[room_id]) >= 2:
                    await websocket.send(json.dumps({"type": "error", "message": "Room full"}))
                    return
                
                rooms[room_id].append(websocket)
                print(f"Client registered in room: {room_id} (Total: {len(rooms[room_id])})")
                
            elif room_id:
                # Relay the message to the other person in the room
                other_clients = [ws for ws in rooms[room_id] if ws != websocket]
                for client in other_clients:
                    await client.send(message)
            else:
                await websocket.send(json.dumps({"type": "error", "message": "Not registered in a room"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if room_id and room_id in rooms:
            if websocket in rooms[room_id]:
                rooms[room_id].remove(websocket)
            if not rooms[room_id]:
                del rooms[room_id]
        print(f"Client disconnected from room: {room_id}")

async def main():
    port = 8765
    print(f"Relay Server starting on port {port}...")
    async with websockets.serve(handle_client, "0.0.0.0", port):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())
