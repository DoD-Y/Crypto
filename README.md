# CryptoTest Lab — NIST Randomness Test Platform

A web-based platform for evaluating random number generators using the NIST Statistical Test Suite (STS).

## Features

- Upload binary sequences and run all 15 NIST statistical tests
- Custom test selection mode
- Real-time results display
- Supports both local WSL (Windows) and VPS (Linux) deployment

## Project Structure

```
├── web_include/           # Web application
│   ├── main.py            # FastAPI backend
│   ├── config.example.py  # Configuration template
│   ├── templates/
│   │   └── index.html     # Frontend UI
│   └── sts-2.1.2/         # NIST STS suite (assess + source)
├── nistgen.py             # Random data generator for NIST testing
├── rand-C.c               # C random number generator source
└── README.md
```

## Quick Start

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd CryptoDZY
cp web_include/config.example.py web_include/config.py
```

Edit `web_include/config.py` with your NIST STS path.

### 2. Install dependencies

```bash
pip install fastapi uvicorn python-multipart
```

### 3. Run the server

```bash
cd web_include
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000` in your browser.

## Configuration

Copy `config.example.py` to `config.py` and set:

- `NIST_DIR` — Path to the NIST STS directory (Linux/VPS)
- `NIST_DIR_WIN` — Windows path via `\\wsl.localhost\...` (Windows WSL only)
- `NIST_DIR_WSL` — Linux path inside WSL (Windows WSL only)

## Deployment

See [deployment guide](DEPLOY.md) for VPS setup with Nginx + HTTPS.

## Security Notes

- The `config.py` file contains local paths and is excluded from git
- Always set up HTTPS and API authentication for public deployments
- Temporary files and test results are cleaned after each request
