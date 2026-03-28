# Secure P2P Encrypted Chat

A robust, terminal-based peer-to-peer (P2P) chat application featuring end-to-end encryption (E2EE) and secure file sharing. Built for privacy-conscious communication directly between users.

---

## 🚀 Features

- **End-to-End Encryption (E2EE):** All messages and files are encrypted using Fernet (AES-128 in CBC mode with HMAC) ensuring only the intended recipient can read them.
- **Smart Key Derivation:** Securely derives a shared encryption key based on the mobile numbers of both peers, eliminating the need for manual key exchange.
- **P2P Architecture:** Direct communication between users without a central messaging server, enhancing privacy and reducing latency.
- **Secure File Sharing:** Integrated support for sending files of any type over the encrypted P2P channel.
- **Modern Terminal UI:** A clean, interactive, and responsive interface powered by the `rich` library.

---

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/beingprogrammed/terminal-chat.git
   cd chat_app
   ```

2. **(Optional) Create a virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 📖 How to Use

1. **Start the Application:**

   ```bash
   python main.py
   ```

2. **Registration:**
   Enter your mobile number when prompted. This is used locally for session identification and key derivation.

3. **Establish Connection:**
   - Enter your **Peer's mobile number**. Both users must enter each other's numbers to correctly derive the shared encryption key.
   - Coordinate roles: One user must choose **(H)ost** to listen for connections, and the other must choose **(J)oin** to initiate the connection.

4. **Chatting:**
   - Type messages and press `Enter` to send.
   - Use the command `/file <path>` to send a file to your peer.
   - Use `/exit` to safely close the connection and quit the app.

---

## 🌐 Connectivity & Deployment

Since this is a direct P2P application, the **Host** must be network-reachable. If you are behind a router or firewall, consider these options:

### 1. Tailscale (Easiest & Most Secure)

- Both users install [Tailscale](https://tailscale.com/).
- Use the provided Tailscale IP (e.g., `100.x.y.z`) to connect.
- Works seamlessly through NAT and firewalls without configuration.

### 2. Ngrok (Quick Public Access)

- The Host runs: `ngrok tcp 8765`
- The Joiner connects using the address provided by Ngrok (e.g., `0.tcp.ngrok.io:12345`).

### 3. Port Forwarding

- Configure your router to forward TCP port `8765` to your local machine's IP.
- The Joiner connects using your **Public IP address**.

### 4. Cloud VPS

- Run the "Host" instance on a cloud provider (AWS, DigitalOcean, etc.).
- Ensure port `8765` is open in the security group/firewall settings.

---

## 🔒 Technical Details

- **Encryption:** Uses the `cryptography` library's Fernet implementation for high-level symmetric encryption.
- **Networking:** Utilizes Python's `asyncio` and `websockets` (or standard socket-based P2P depending on implementation) for real-time, asynchronous communication.
- **UI:** Leveraging `rich` for live-updating layouts, formatted text, and progress bars during file transfers.

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.
