import asyncio
import sys
import os
import cv2
from storage_utils import LocalStorage
from crypto_utils import CryptoManager
from network_utils import Peer
from ui_utils import TerminalUI, console
from rich.panel import Panel
from media_utils import frame_to_ascii, AudioManager

ui = TerminalUI()
audio_manager = AudioManager()
call_active = False

async def handle_received_message(data):
    if data['type'] == 'text':
        ui.display_message("Peer", data['content'])
    elif data['type'] == 'file':
        filename = data['filename']
        file_data = data['content']
        saved_path = ui.save_file(filename, file_data)
        ui.display_message("Peer", f"Saved to {saved_path}", msg_type="file")
    elif data['type'] == 'media':
        if data['media_type'] == 'video':
            ui.display_video(data['content'])
        elif data['media_type'] == 'audio':
            audio_manager.play_chunk(data['content'])

async def video_call_task(peer):
    cap = cv2.VideoCapture(0)
    while call_active:
        ret, frame = cap.read()
        if ret:
            ascii_frame = frame_to_ascii(frame)
            await peer.send_media("video", ascii_frame)
        await asyncio.sleep(0.1)  # ~10 FPS
    cap.release()

async def audio_call_task(peer):
    audio_manager.start_recording()
    while call_active:
        chunk = audio_manager.get_chunk()
        if chunk:
            await peer.send_media("audio", chunk)
        await asyncio.sleep(0.01)

async def chat_loop(peer, user_data):
    global call_active
    ui.refresh()
    while True:
        try:
            user_input = await ui.get_input()
            if not user_input:
                continue

            if user_input.startswith("/file "):
                file_path = user_input.replace("/file ", "").strip()
                if os.path.exists(file_path):
                    await peer.send_file(file_path)
                    ui.display_message("Me", f"Sent file: {os.path.basename(file_path)}", msg_type="file")
                else:
                    console.print(f"[bold red]Error:[/] File {file_path} not found.")
            elif user_input == "/call":
                if not call_active:
                    call_active = True
                    asyncio.create_task(video_call_task(peer))
                    asyncio.create_task(audio_call_task(peer))
                    ui.display_message("System", "Started Video/Audio call.")
            elif user_input == "/stop":
                call_active = False
                ui.display_video("")  # Clear video
                ui.display_message("System", "Stopped call.")
            elif user_input == "/exit":
                break
            else:
                await peer.send_text(user_input)
                ui.display_message("Me", user_input)
        except Exception as e:
            console.print(f"[bold red]Error:[/] {str(e)}")
            break

async def main():
    # 1. Registration (WhatsApp-style: Number first)
    user_data = None
    if LocalStorage.is_registered():
        user_data = LocalStorage.get_user_data()
        console.print(f"Existing profile found: [bold green]{user_data['mobile_number']}[/] ([dim]{user_data['name']}[/])")
        use_existing = input("Use this profile? (Y/n): ").strip().lower()
        if use_existing == 'n':
            user_data = None

    if not user_data:
        console.print(Panel("Welcome! Let's get started with your mobile number.", title="ChatApp Registration", border_style="bold green"))
        mobile = input("Enter your mobile number: ")
        name = input("Enter your display name: ")
        user_data = LocalStorage.save_user_data(mobile, name)
    
    console.print(f"Logged in as: [bold green]{user_data['mobile_number']}[/] ([dim]{user_data['name']}[/])")

    # 2. Encryption Setup
    console.print("\n[bold yellow]Step 2: Encryption Setup[/]")
    peer_mobile = input("Enter Peer's mobile number: ").strip()
    while not peer_mobile:
        peer_mobile = input("[bold red]Peer number is required![/] Enter Peer's mobile number: ").strip()
    
    combined_secret = "".join(sorted([user_data['mobile_number'], peer_mobile]))
    crypto = CryptoManager(key=combined_secret)

    # 3. Mode (Host or Join)
    choice = input("\nDo you want to (H)ost or (J)oin? ").strip().upper()
    peer = Peer(crypto_manager=crypto)
    peer.set_on_message(handle_received_message)

    if choice == 'H':
        console.print("Waiting for peer to connect...")
        server_task = asyncio.create_task(peer.start_server())
        await peer.connection_event.wait()
        console.print("[bold green]Peer connected![/]")
        await chat_loop(peer, user_data)
    elif choice == 'J':
        peer_ip = input("Enter Peer IP (default 127.0.0.1): ") or "127.0.0.1"
        try:
            await peer.connect_to_peer(peer_ip)
            await chat_loop(peer, user_data)
        except Exception as e:
            console.print(f"[bold red]Connection failed:[/] {str(e)}")
    else:
        console.print("Invalid choice. Exiting.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
