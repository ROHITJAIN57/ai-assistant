# HuggingFace Chatbot 🤖

An interactive AI chatbot built with HuggingFace Transformers. Uses state-of-the-art language models for natural conversation.

## Quick Start

### Prerequisites
- Python 3.10+
- Virtual environment (already created)

### Installation

1. **Activate Virtual Environment**:
```bash
.\venv\Scripts\Activate.ps1
```

2. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

### Usage

Run the chatbot:
```bash
python src/main.py
```

**Available Models**:
- `gpt2` - Fast, lightweight (default)
- `gpt2-medium` - Balanced quality/speed
- `distilgpt2` - Ultra-lightweight
- `facebook-opt` - Modern architecture
- `microsoft-phi` - Efficient and capable

### Commands

In the chat:
- Type your message and press Enter to chat
- Type `exit` or `quit` to end conversation
- Type `clear` to clear chat history

## Project Structure

```
gen_ai_project/
├── src/
│   ├── main.py              ← Chatbot application
│   └── __init__.py
├── utils/
│   ├── config.py            ← Configuration
│   ├── logger.py            ← Logging setup
│   ├── model_utils.py       ← Model utilities
│   └── __init__.py
├── .env                     ← Configuration (your API keys)
├── requirements.txt         ← Dependencies
└── venv/                    ← Virtual environment
```

## Configuration

Edit `.env` file to customize:
```
LOG_LEVEL=INFO              # INFO, DEBUG, WARNING, ERROR
DEVICE=auto                 # auto, cpu, cuda
HF_MODEL=gpt2              # Model name
MAX_LENGTH=100             # Response length
TEMPERATURE=0.7            # Randomness (0-1)
USE_GPU=true              # Use GPU if available
```

## Features

✅ Interactive chat interface
✅ Multiple HuggingFace models
✅ Conversation history
✅ Auto GPU/CPU detection
✅ Configurable settings
✅ Comprehensive logging

## Performance Tips

- **Faster responses**: Use smaller models (gpt2, distilgpt2)
- **GPU acceleration**: CUDA-enabled PyTorch for NVIDIA GPUs
- **Lower memory**: Use CPU mode (set DEVICE=cpu)

## Requirements

- transformers >= 4.37
- torch >= 2.2
- python-dotenv >= 1.0

See `requirements.txt` for full list.

---

**Ready to chat!** Run `python src/main.py` 🚀
