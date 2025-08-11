# Language Detective Service 🕵️‍♂️

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68+-00a393.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

> A powerful multi-provider audio language detection service that identifies spoken languages in real-time using AI providers like Google Gemini, Sarvam AI, OpenAI, and ElevenLabs.

## ✨ Features

🚀 **Multi-Provider Support** - Integrates with Google Gemini, ElevenLabs, Sarvam AI(mock), OpenAI (mock). 
⚡ **Real-time Detection** - Concurrent execution across all providers for optimal performance  
💰 **Cost Estimation** - Provides estimated costs and token usage for each provider  
📊 **Comprehensive Metrics** - Tracks timing, success rates, and error handling  
🇮🇳 **Indian Language Support** - Optimized for detecting Indian languages (Hindi, Tamil, Telugu, etc.)  
🌐 **RESTful API** - Clean FastAPI endpoints with automatic documentation  

## 🏗️ Architecture

```
src/
├── connectors/          # Provider connectors
│   ├── base.py         # Base connector class
│   ├── gemini.py       # Google Gemini (real implementation)
│   ├── sarvam.py       # Sarvam AI (mock implementation)
│   ├── openai_mock.py  # OpenAI (mock implementation)
│   └── elevenlabs_mock.py # ElevenLabs (real implementation)
├── models.py           # Pydantic data models
├── coordinator.py      # Orchestrates all providers
└── main.py            # FastAPI application
```

## 🔧 Prerequisites

- Python 3.10+
- UV package manager (recommended) or pip
- API keys for Google Gemini and Eleven Labs

## 🚀 Quick Start

### Option 1: Using UV (Recommended)

```bash
# Install UV
pip install uv

# Clone and setup
git clone <repository-url>
cd language-detective
uv sync
```

### Option 2: Using pip

```bash
git clone <repository-url>
cd language-detective
pip install -r requirements.txt
```

## ⚙️ Configuration

1. **Create environment file**:
   ```bash
   cp env.example .env
   ```

2. **Add your API keys** to `.env`:
   ```env
   GEMINI_API_KEY=your_actual_gemini_api_key
   ELEVENLABS_API_KEY=your-key
   ```

## 🎯 Usage

### Starting the Service

```bash
# Using UV
uv run src/main.py

# Using Python directly
python -m src.main
```

🌐 **Service URL**: `http://localhost:8000`  
📚 **API Docs**: `http://localhost:8000/docs`

### API Endpoints

#### 🔍 Language Detection (All Providers)
```http
POST /detect/language
```

**Request**:
```json
{
  "audio_file_path": "/path/to/audio.wav",
  "ground_truth_language": "hi"
}
```

**Response**:
```json
{
  "results": [
    {
      "provider_name": "Google Gemini",
      "detected_language": "hi",
      "time_taken": 1.234,
      "estimated_cost": {
        "tokens": 150,
        "dollars": 0.000015
      },
      "status": "success",
      "error_message": null
    }
  ],
  "total_time": 2.456,
  "successful_providers": 4,
  "failed_providers": 0
}
```

#### 🎯 Single Provider Detection
```http
POST /detect/language/{provider_name}
```

#### 📋 List Available Providers
```http
GET /providers
```

#### ❤️ Health Check
```http
GET /health
```

## 🎵 Supported Audio Formats

| Format | Extension | Status |
|--------|-----------|---------|
| WAV    | `.wav`    | ✅ Supported |
| MP3    | `.mp3`    | ✅ Supported |
| M4A    | `.m4a`    | ✅ Supported |
| FLAC   | `.flac`   | ✅ Supported |
| OGG    | `.ogg`    | ✅ Supported |
| AAC    | `.aac`    | ✅ Supported |

## 🌍 Supported Languages

### 🇮🇳 Indian Languages
| Language | Code | Language | Code |
|----------|------|----------|------|
| Hindi    | `hi` | Bengali  | `bn` |
| Tamil    | `ta` | Marathi  | `mr` |
| Telugu   | `te` | Gujarati | `gu` |
| Kannada  | `kn` | Punjabi  | `pa` |
| Malayalam| `ml` | Urdu     | `ur` |

### 🌐 International Languages
| Language | Code | Language | Code |
|----------|------|----------|------|
| English  | `en` | Chinese  | `zh` |
| French   | `fr` | Japanese | `ja` |
| German   | `de` | Korean   | `ko` |
| Spanish  | `es` | Arabic   | `ar` |
| Russian  | `ru` |          |      |

## ⚠️ Error Handling

The service provides comprehensive error handling:

- **🚫 File Not Found**: Returns 400 if audio file doesn't exist
- **📁 Unsupported Format**: Returns 400 for unsupported audio formats  
- **🔌 API Errors**: Captures and reports provider-specific errors
- **🌐 Network Issues**: Handles timeouts and connection failures gracefully

## ⚡ Performance Features

- **🔄 Concurrent Execution**: All providers run simultaneously
- **⏰ Timeout Handling**: Configurable timeouts for each provider
- **🛡️ Error Isolation**: One provider failure doesn't affect others
- **💸 Cost Tracking**: Real-time cost estimation for each operation

## 🛠️ Development

### Running Tests
```bash
# Using UV
uv run pytest

# Using pip
pytest
```

### Code Formatting
```bash
# Using UV
uv run black src/
uv run flake8 src/

# Using pip
black src/
flake8 src/
```

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Make** your changes
4. **Add** tests for your changes
5. **Commit** your changes (`git commit -m 'Add amazing feature'`)
6. **Push** to the branch (`git push origin feature/amazing-feature`)
7. **Submit** a pull request

## 📄 License

This project is part of the DripLink BE Intern Assignment.

## 📞 Support

For questions or issues, please:
- 📧 Contact the development team
- 📖 Refer to the assignment documentation
- 🐛 Open an issue on GitHub

---

