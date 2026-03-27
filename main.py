import asyncio
import sys
import os
import hashlib
import json
import urllib.request
import urllib.parse
from storage_utils import LocalStorage
from crypto_utils import CryptoManager
from network_utils import Peer
from ui_utils import TerminalUI, console
from rich.panel import Panel

ui = TerminalUI()

# Default relay server
DEFAULT_RELAY = "ws://localhost:8765" 
# Simple public discovery service (Anonymous KV store)
# This allows peers to find the relay URL automatically if one of them enters it.
DISCOVERY_API = "https://keyvalue.xyz/12c1e4c7/room_"

def publish_relay_url(room_hash, url):
    """Saves the relay URL to a public discovery service."""
    try:
        data = url.encode('utf-8')
        req = urllib.request.Request(f"{DISCOVERY_API}{room_hash}", data=data, method='POST')
        with urllib.request.urlopen(req) as f:
            pass
    except:
        pass # Silent fail if discovery service is down

def fetch_relay_url(room_hash):
    """Attempts to find a relay URL published by the peer."""
    try:
        with urllib.request.urlopen(f"{DISCOVERY_API}{room_hash}") as f:
            url = f.read().decode('utf-8').strip()
            return url if url and "://" in url else None
    except:
        return None

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
        use_existing = input("Use this profile? (Y/n): ").strip().lower() or 'y'
        if use_existing == 'n':
            user_data = None
    
    if not user_data or not user_data.get('mobile_number'):
        console.print(Panel("Welcome! Let's get started.", title="ChatApp Registration", border_style="bold green"))
        mobile = input("Enter your mobile number: ")
        name = input("Enter your display name: ")
        user_data = LocalStorage.save_user_data(mobile, name)
    
    console.print(f"Logged in as: [bold green]{user_data['mobile_number']}[/] ([dim]{user_data['name']}[/])")

    # 2. Peer Setup
    console.print("\n[bold yellow]Step 2: Peer Setup[/]")
    peer_mobile = input("Enter Peer's mobile number: ").strip()
    while not peer_mobile:
        peer_mobile = input("[bold red]Peer number is required![/] Enter Peer's mobile number: ").strip()
    
    combined_secret = "".join(sorted([user_data['mobile_number'], peer_mobile]))
    room_hash = hashlib.sha256(combined_secret.encode()).hexdigest()[:16]
    crypto = CryptoManager(key=combined_secret)

    # 3. Automatic Discovery & Connection
    # First, check if a relay URL is already saved locally
    relay_url = LocalStorage.get_relay_url()
    
    # If not saved locally, try to "Discover" it from the public service
    if not relay_url:
        console.print("[dim]Searching for peer's room...[/]")
        relay_url = fetch_relay_url(room_hash)
    
    # If still not found, ask for it once
    if not relay_url:
        console.print("\n[bold cyan]Relay Server Setup (One-time)[/]")
        relay_url = input(f"Enter Relay Server URL (default {DEFAULT_RELAY}): ") or DEFAULT_RELAY
        LocalStorage.save_relay_url(relay_url)
        # Publish it so the peer can find it automatically
        publish_relay_url(room_hash, relay_url)

    peer = Peer(crypto_manager=crypto)
    peer.set_on_message(handle_received_message)

    console.print(f"Connecting to [bold cyan]{peer_mobile}[/]...")
    try:
        await peer.connect_to_relay(relay_url, room_hash)
        # Also ensure it's published upon successful connection
        publish_relay_url(room_hash, relay_url)
        await chat_loop(peer, user_data)
    except Exception as e:
        console.print(f"[bold red]Connection failed:[/] {str(e)}")
        # Reset saved URL if it was invalid to allow re-entry
        if "isn't a valid URI" in str(e):
             LocalStorage.save_relay_url("") 

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
