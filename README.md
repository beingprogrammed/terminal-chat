# P2P Encrypted Chat App

A secure, peer-to-peer chat application with automatic key derivation based on mobile numbers.

## Features
- **End-to-End Encryption:** Uses Fernet (AES-128).
- **Smart Key Derivation:** No need to share keys manually. The app derives a shared secret by combining your number and your peer's number.
- **File Sharing:** Send files securely over the encrypted channel.
- **Terminal UI:** Beautiful interface using `rich`.

## Installation

1. **Clone the repository.**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## How to Use

1. **Run the app:** `python main.py`
2. **Register:** Enter your mobile number.
3. **Setup:** Enter your **Peer's mobile number**. (Both sides must do this).
4. **Connect:** One person chooses **(H)ost**, the other **(J)oin**.

---

## Deployment (Making it Public)

Since this is P2P, the "Host" must be reachable. If you are behind a home router, use one of these:

### Option A: Tailscale (Recommended)
1. Both users install [Tailscale](https://tailscale.com/).
2. Use the Tailscale IP (starts with `100.`) to connect.
3. **Benefit:** Works through any firewall/router automatically.

### Option B: Ngrok (Quick Public Access)
1. Download [Ngrok](https://ngrok.com/).
2. Run: `ngrok tcp 8765`
3. The Joiner uses the address provided (e.g., `0.tcp.ngrok.io`).

### Option C: Port Forwarding
1. Access router settings.
2. Forward port `8765` to your local IP.
3. The Joiner uses your **Public IP**.

### Option D: Cloud VPS
1. Run the "Host" on a server (AWS, DigitalOcean, etc.).
2. Ensure port `8765` is open in the server's security group/firewall.
