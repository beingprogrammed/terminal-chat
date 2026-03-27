import asyncio
import sys
import os
from storage_utils import LocalStorage
from crypto_utils import CryptoManager
from network_utils import Peer
from ui_utils import TerminalUI, console
from rich.panel import Panel

ui = TerminalUI()

# Default relay server (User can change this to their own VPS IP/Domain)
DEFAULT_RELAY = "ws://localhost:8765" 

async def handle_received_message(data):
    if data['type'] == 'text':
        ui.display_message("Peer", data['content'])
    elif data['type'] == 'file':
        filename = data['filename']
        file_data = data['content']
        saved_path = ui.save_file(filename, file_data)
        ui.display_message("Peer", f"Received file: {filename} -> {saved_path}", msg_type="file")

async def chat_loop(peer, user_data):
    ui.refresh()
    while True:
        try:
            user_input = await ui.get_input()
            if not user_input:
                continue

            if user_input.startswith("/file "):
                file_path = user_input.replace("/file ", "").strip()
                if os.path.exists(file_path):
                    ui.display_message("Me", f"Sending file: {os.path.basename(file_path)}...", msg_type="file")
                    await peer.send_file(file_path)
                else:
                    console.print(f"[bold red]Error:[/] File {file_path} not found.")
            elif user_input == "/exit":
                break
            else:
                await peer.send_text(user_input)
                ui.display_message("Me", user_input)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            break

async def main():
    # 1. Registration
    user_data = None
    if LocalStorage.is_registered():
        user_data = LocalStorage.get_user_data()
        console.print(f"Existing profile found: [bold green]{user_data['mobile_number']}[/] ([dim]{user_data['name']}[/])")
        use_existing = input("Use this profile? (Y/n): ").strip().lower()
        if use_existing == 'n':
            user_data = None

    if not user_data:
        console.print(Panel("Welcome! Let's get started.", title="ChatApp Registration", border_style="bold green"))
        mobile = input("Enter your mobile number: ")
        name = input("Enter your display name: ")
        user_data = LocalStorage.save_user_data(mobile, name)
    
    console.print(f"Logged in as: [bold green]{user_data['mobile_number']}[/] ([dim]{user_data['name']}[/])")

    # 2. Encryption Setup
    console.print("\n[bold yellow]Step 2: Peer Setup[/]")
    peer_mobile = input("Enter Peer's mobile number: ").strip()
    while not peer_mobile:
        peer_mobile = input("[bold red]Peer number is required![/] Enter Peer's mobile number: ").strip()
    
    combined_secret = "".join(sorted([user_data['mobile_number'], peer_mobile]))
    crypto = CryptoManager(key=combined_secret)

    # 3. Mode (Local or Global)
    console.print("\n[bold cyan]How do you want to connect?[/]")
    console.print("1. [bold]Local P2P[/] (Same network, fast)")
    console.print("2. [bold]Global Relay[/] (Over the internet, needs a relay server)")
    conn_type = input("Choose (1/2): ").strip()

    peer = Peer(crypto_manager=crypto)
    peer.set_on_message(handle_received_message)

    if conn_type == '1':
        choice = input("Do you want to (H)ost or (J)oin? ").strip().upper()
        if choice == 'H':
            console.print("Waiting for local peer to connect...")
            server_task = asyncio.create_task(peer.start_server())
            await peer.connection_event.wait()
            console.print("[bold green]Peer connected locally![/]")
            await chat_loop(peer, user_data)
        elif choice == 'J':
            peer_ip = input("Enter Peer IP (default 127.0.0.1): ") or "127.0.0.1"
            try:
                await peer.connect_to_peer(peer_ip)
                await chat_loop(peer, user_data)
            except Exception as e:
                console.print(f"[bold red]Connection failed:[/] {str(e)}")
    else:
        relay_url = input(f"Enter Relay Server URL (default {DEFAULT_RELAY}): ") or DEFAULT_RELAY
        # Room ID is derived from combined mobile numbers so both peers join the same room automatically
        room_id = hashlib.sha256(combined_secret.encode()).hexdigest()[:16]
        console.print(f"Connecting to relay room...")
        try:
            await peer.connect_to_relay(relay_url, room_id)
            console.print(f"[bold green]Connected to Relay![/] Room ID: {room_id}")
            await chat_loop(peer, user_data)
        except Exception as e:
            console.print(f"[bold red]Relay Connection failed:[/] {str(e)}")

if __name__ == "__main__":
    import hashlib # Needed for room_id
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
