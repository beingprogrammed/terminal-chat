import asyncio
import os
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.live import Live
from rich.table import Table
from rich.layout import Layout

console = Console()

class TerminalUI:
    def __init__(self):
        self.messages = []
        self.downloads_dir = "downloads"
        if not os.path.exists(self.downloads_dir):
            os.makedirs(self.downloads_dir)

    def display_message(self, sender, content, msg_type="text"):
        if msg_type == "text":
            self.messages.append(f"[bold blue]{sender}:[/] {content}")
        elif msg_type == "file":
            self.messages.append(f"[bold green]{sender} sent a file:[/] [underline]{content}[/]")
        self.refresh()

    def refresh(self):
        # Clear terminal and re-render
        console.clear()
        
        # Chat Table
        chat_table = Table(show_header=False, box=None, expand=True)
        chat_table.add_column("Message")
        for msg in self.messages[-15:]:
            chat_table.add_row(msg)
        
        console.print(Panel(chat_table, title="P2P Encrypted Chat", subtitle="Type '/file <path>' to send files | '/exit' to quit", border_style="bold magenta"))

    async def get_input(self):
        return await asyncio.to_thread(input, "> ")

    def save_file(self, filename, data):
        path = os.path.join(self.downloads_dir, filename)
        with open(path, "wb") as f:
            f.write(data)
        return path
