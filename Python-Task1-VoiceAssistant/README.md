# Nova — Intelligent Python Voice Assistant

Nova is a modular, production-grade, portfolio-quality Python Intelligent Voice Assistant built with real-time Speech-to-Text (STT) input, offline Text-to-Speech (TTS) synthesis, vector-space Natural Language Understanding (NLU), live weather lookup, Wikipedia general knowledge Q&A, voice-controlled SMTP email dispatch, and non-blocking background timed reminders.

---

## 📋 Table of Contents

1. [Project Overview](#-project-overview)
2. [Features Overview](#-features-overview)
3. [Beginner Features](#-beginner-features)
4. [Advanced Features](#-advanced-features)
5. [System Architecture & Flow Diagram](#-system-architecture--flow-diagram)
6. [Project Structure & File Index](#-project-structure--file-index)
7. [Technology Stack](#-technology-stack)
8. [How It Works](#-how-it-works)
9. [Installation & Prerequisites](#-installation--prerequisites)
10. [Virtual Environment Setup](#-virtual-environment-setup)
11. [Dependency Installation](#-dependency-installation)
12. [Environment Configuration](#-environment-configuration)
13. [OpenWeatherMap API Setup Guide](#-openweathermap-api-setup-guide)
14. [Email SMTP Setup Guide](#-email-smtp-setup-guide)
15. [Running the Assistant](#-running-the-assistant)
16. [System Readiness Check](#-system-readiness-check)
17. [Voice Command Examples](#-voice-command-examples)
18. [Custom Commands System](#-custom-commands-system)
19. [Timed Reminders System](#-timed-reminders-system)
20. [Voice Email Dispatch & Stateful Prompts](#-voice-email-dispatch--stateful-prompts)
21. [Live Weather Lookup](#-live-weather-lookup)
22. [Wikipedia General Knowledge Q&A](#-wikipedia-general-knowledge-qa)
23. [Error Handling & Resiliency Safeguards](#-error-handling--resiliency-safeguards)
24. [Privacy Policy & Data Processing](#-privacy-policy--data-processing)
25. [Security Safeguards](#-security-safeguards)
26. [Automated Testing & Verification](#-automated-testing--verification)
27. [Troubleshooting Guide](#-troubleshooting-guide)
28. [System Limitations](#-system-limitations)
29. [Future Roadmap](#-future-roadmap)
30. [Project Status](#-project-status)

---

## 🌟 Project Overview

Nova is designed as an extensible, modular voice assistant written in clean, type-annotated Python. Unlike rigid keyword-matching bots or heavy LLM-dependent wrappers, Nova combines a lightweight **Vector Space NLU Model (TF-IDF + Cosine Similarity)** with decoupled entity extraction and service-oriented command dispatching.

Nova demonstrates modern software engineering best practices:
- **Service-Oriented Architecture (SOA)** with complete Separation of Concerns (SoC).
- **Environment-based credential safety** ensuring secrets are never hardcoded or printed.
- **Asynchronous background task execution** for timed alerts without thread blocking.
- **Stateful multi-turn dialog flow** for interactive follow-up inputs.
- **Comprehensive test suite** covering hardware mocks, network mocks, security validation, and end-to-end command routing.

---

## ⚙️ Features Overview

- **Real-Time Voice I/O**: High-accuracy microphone capture with ambient noise calibration and pyttsx3 offline voice synthesis.
- **Intent Recognition & NLU**: TF-IDF vector matching capable of recognizing natural variations for 9 distinct intents.
- **Entity Extraction**: Decoupled regex-based extractor parsing cities, topics, emails, messages, and reminder durations.
- **Live Weather Lookup**: Real-time current weather metrics (°C, feels-like, humidity, condition, wind speed) via OpenWeatherMap.
- **Wikipedia Knowledge Q&A**: Automatic extraction of topics and concise 1-2 sentence spoken summaries from Wikipedia REST API.
- **Voice-Controlled Email**: TLS-secured SMTP mail delivery with multi-step interactive prompts for missing recipient or body content.
- **Timed Background Reminders**: Non-blocking `threading.Timer` alerts with audible TTS notifications.
- **Custom User Commands**: Safe JSON-configured custom commands (`open_url`, `response`).
- **Non-Interactive Verification**: Command-line readiness check (`python main.py --check`) for automated environment validation.

---

## 🐣 Beginner Features

- **Time & Date Queries**: Local dynamic time (`"what time is it"`) and formatted calendar date (`"what is today's date"`).
- **Time-Appropriate Greetings**: Dynamic greetings based on system clock (*Good morning*, *Good afternoon*, *Good evening*).
- **Automated Web Search**: Direct browser launching for search queries (*"search the web for FastAPI documentation"*).
- **Terminal Fallback Input**: Graceful degradation to command-line text input if no microphone hardware is detected.

---

## 🚀 Advanced Features

- **Vector Space NLU Model**: Cosine similarity scoring over TF-IDF n-gram pattern matrices with confidence thresholding (default `0.45`).
- **Stateful Context Manager**: `CommandRouter` maintains `pending_context` across turns to handle multi-step dialogs (e.g. asking for missing email recipients or weather locations).
- **Safe Secret Sanitization**: Secrets validator that blocks dummy placeholder keys and redacts credentials from logs.
- **Asynchronous Timer Engine**: Background daemon threads for scheduling reminders concurrently without blocking the STT listener loop.
- **Zero-Shell Execution Safeguard**: Custom command validator prohibiting `eval()`, `exec()`, arbitrary shell execution, or non-http(s) URL schemes.

---

## 📐 System Architecture & Flow Diagram

The complete end-to-end processing pipeline operates through standard modular interfaces:

```
┌─────────────────┐
│   Microphone    │
└────────┬────────┘
         │ (Analog Audio)
         ▼
┌─────────────────┐
│ Speech Recogn.  │  (Google Speech Recognition API / Terminal Fallback)
└────────┬────────┘
         │ (Clean Text String)
         ▼
┌─────────────────┐
│  NLU Engine     │  (TF-IDF Vectorizer + Cosine Similarity Classifier)
└────────┬────────┘
         │ (Intent Label & Confidence Score)
         ▼
┌─────────────────┐
│ Entity Extractor│  (Extracts cities, query targets, email addrs, durations)
└────────┬────────┘
         │ (Intent + Structured Entities Dict)
         ▼
┌─────────────────┐
│ Command Router  │  (Manages stateful pending_context follow-ups & service dispatch)
└────────┬────────┘
         │
 ┌───────┴────────────────────────────────────────────────────────┐
 │ Direct Service Dispatch                                        │
 ▼                                                                ▼
┌───────────────────────┐                                ┌───────────────────────┐
│   Domain Services     │                                │   External APIs /     │
│ (DateTime, Weather,   │ ◄────────────────────────────► │   Network Protocols   │
│  Knowledge, Email,    │                                │ (OpenWeatherMap,      │
│  Reminder, Custom)    │                                │  Wikipedia, SMTP)     │
└────────┬──────────────┘                                └───────────────────────┘
         │ (Response Text & Exit Flag)
         ▼
┌─────────────────┐
│ Text-To-Speech  │  (pyttsx3 Voice Synthesizer / Terminal Output)
└────────┬────────┘
         │ (Spoken Audio Output)
         ▼
┌─────────────────┐
│      User       │
└─────────────────┘
```

---

## 📁 Project Structure & File Index

```
Voice Assistant/
│
├── .env.example            # Configuration & secret placeholders template
├── .gitignore              # Git exclusions for secrets, caches, and logs
├── README.md               # Complete portfolio documentation & privacy policy
├── requirements.txt        # Python runtime & testing dependencies manifest
├── main.py                 # Application entry point, voice loop, & --check runner
├── config.py               # Centralized configuration & secret safety layer
│
├── config/
│   └── custom_commands.json# User custom commands JSON configuration registry
│
├── core/                   # Drivers & Pipeline Orchestration
│   ├── logger.py           # Structured application logging driver
│   ├── stt.py              # Speech-to-Text driver with noise calibration & fallback
│   ├── tts.py              # pyttsx3 voice synthesizer with dynamic voice selection
│   └── command_router.py   # Central command routing pipeline & context manager
│
├── nlp/                    # Natural Language Understanding Subsystem
│   ├── intent_engine.py    # Vector Space NLP matcher (TF-IDF + Cosine Similarity)
│   ├── entity_extractor.py  # Named entity, city, email, & duration extractor
│   └── intents.json        # Intent dataset & natural language pattern training
│
├── services/               # Modular Skills & Domain Actions
│   ├── datetime_service.py # Time, date, and greetings service
│   ├── search_service.py   # Web search provider with regex query extraction
│   ├── custom_service.py   # Custom command validator & safe executor
│   ├── weather_service.py  # Live OpenWeatherMap API current weather provider
│   ├── knowledge_service.py# Wikipedia Q&A general knowledge lookup provider
│   ├── email_service.py    # Secure SMTP email dispatch engine
│   └── reminder_service.py # Non-blocking background thread timer engine
│
└── tests/                  # Automated Unit & Integration Test Suite
    ├── test_foundation.py  # Phase 1 foundation verification suite
    ├── test_phase2.py      # Phase 2 core speech I/O & basic service tests
    ├── test_phase3.py      # Phase 3 advanced NLU, entities, & custom command tests
    ├── test_phase4.py      # Phase 4 weather API & knowledge Q&A tests
    ├── test_phase5.py      # Phase 5 email automation & reminder tests
    └── test_phase6.py      # Phase 6 security, logging, error handling, & pipeline tests
```

---

## 💻 Technology Stack

| Layer | Component / Tool | Responsibility |
| :--- | :--- | :--- |
| **Language** | Python 3.10+ | Core application logic, type annotations, OOP architecture |
| **Speech Recognition** | `SpeechRecognition` | Audio capture, energy threshold calibration, Google STT API |
| **Text-to-Speech** | `pyttsx3` | Offline voice synthesis and speech output |
| **Audio Driver** | `PyAudio` | PortAudio bindings for microphone input stream capture |
| **NLP / Machine Learning** | `scikit-learn` | `TfidfVectorizer` & `cosine_similarity` matrix classification |
| **Environment Config** | `python-dotenv` | Loading `.env` key-value pairs safely |
| **HTTP Requests** | `requests` | REST API requests to OpenWeatherMap & Wikipedia |
| **Email Protocol** | `smtplib` / `email.message` | TLS-encrypted SMTP mail dispatch |
| **Concurrency** | `threading.Timer` | Background asynchronous timer execution |
| **Testing** | `unittest` / `unittest.mock` | Automated test runner with hardware & network mocks |

---

## 🛠️ How It Works

1. **Audio Input**: Nova initializes `SpeechToTextEngine`, calibrates for ambient background noise, and listens for voice input.
2. **NLU Processing**: The recognized text string is passed to `IntentClassifier`. The text is vectorized using a pre-fitted TF-IDF model and scored against pattern matrices via cosine similarity.
3. **Entity Extraction**: If the top score exceeds confidence threshold `0.45`, `EntityExtractor` parses structured entities (e.g. city names, query strings, email addresses, reminder durations).
4. **Command Routing**: `CommandRouter` checks for active follow-up dialogs (`pending_context`). If none, it routes the intent and entities to the designated domain service module.
5. **Service Execution**: The service module processes the request (e.g. fetching weather via HTTP, querying Wikipedia REST API, or scheduling a background `threading.Timer`).
6. **Voice Synthesis**: The resulting natural language text is logged and spoken aloud via `TextToSpeechEngine`.

---

## ⚙️ Installation & Prerequisites

### Prerequisites
- Python 3.10 or higher installed.
- Working audio input device (Microphone) and output device (Speakers / Headphones).
- Internet connection (for Google STT decoding, Weather API, Wikipedia API, and SMTP email).

---

## 🐍 Virtual Environment Setup

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-username/nova-voice-assistant.git
   cd nova-voice-assistant
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - **Windows (CMD)**:
     ```cmd
     venv\Scripts\activate.bat
     ```
   - **Linux / macOS**:
     ```bash
     source venv/bin/activate
     ```

---

## 📦 Dependency Installation

Install all required runtime and testing dependencies using `pip`:

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Configuration

1. **Copy Configuration Template**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` File**:
   Open `.env` in any text editor and fill in your actual service credentials. **NEVER commit `.env` to source control.**

---

## 🌤️ OpenWeatherMap API Setup Guide

1. Visit [OpenWeatherMap](https://openweathermap.org/) and create a free user account.
2. Navigate to your Account Dashboard $\rightarrow$ **API Keys**.
3. Copy your generated API key.
4. Add the key to `.env`:
   ```env
   OPENWEATHER_API_KEY=your_actual_openweathermap_api_key_here
   ```

---

## 📧 Email SMTP Setup Guide

To enable voice-controlled email sending via Gmail or another SMTP provider:

1. **Gmail App Password Setup**:
   - Enable 2-Step Verification on your Google Account.
   - Go to **Security** $\rightarrow$ **App Passwords**.
   - Generate a new App Password for "Mail".
2. **Update `.env`**:
   ```env
   EMAIL_SMTP_HOST=smtp.gmail.com
   EMAIL_SMTP_PORT=587
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_16_digit_app_password
   EMAIL_FROM=your_email@gmail.com
   EMAIL_USE_TLS=true
   ```

---

## 🚀 Running the Assistant

### **Interactive Continuous Voice Loop**
Launches Nova's continuous spoken interaction loop:

```bash
python main.py
```

- Speak commands naturally into your microphone.
- Press `Ctrl+C` or say `"exit"` / `"quit"` / `"goodbye"` to stop the assistant cleanly.

---

## 🧪 System Readiness Check

Verify your environment, hardware initialization, NLU patterns, and service configurations in non-interactive mode without speaking into a microphone:

```bash
python main.py --check
```

Sample output:
```text
==========================================
  Nova System Readiness Verification (Phase 6)
==========================================

--- System Services Status ---
Email Service:      NOT CONFIGURED (Add EMAIL_USERNAME and EMAIL_PASSWORD to .env)
Reminder Service:   READY
Weather Service:    READY
Knowledge Service:  READY
NLU Engine:         READY
Speech Recognition: READY
Text-to-Speech:     READY

Input:    'hello'
Result:   Intent='greeting' (Confidence: 1.00, Entities: {})
Output:   Good evening, User! How can I assist you today?

Input:    'what time is it?'
Result:   Intent='get_time' (Confidence: 1.00, Entities: {})
Output:   The current time is 12:30 AM.

System Readiness Verification Complete.
```

---

## 🗣️ Voice Command Examples

| Category | Example User Voice Phrase | Classified Intent | Assistant Output / Action |
| :--- | :--- | :--- | :--- |
| **Greeting** | *"Hello"*, *"Good morning"* | `greeting` | Time-appropriate greeting response |
| **Time** | *"What time is it?"*, *"Tell me the time"* | `get_time` | Spoken current system time |
| **Date** | *"What is today's date?"*, *"What day is it"* | `get_date` | Spoken formatted calendar date |
| **Weather** | *"What's the weather in Pune?"* | `get_weather` | Spoken temperature, humidity, condition & wind speed |
| **Weather** | *"How hot is it in Delhi?"* | `get_weather` | Real-time weather lookup for Delhi |
| **Knowledge** | *"What is Python?"* | `knowledge_query` | Spoken 1-2 sentence Wikipedia summary |
| **Knowledge** | *"What is machine learning?"* | `knowledge_query` | Spoken Wikipedia article extract |
| **Knowledge** | *"Who was Albert Einstein?"* | `knowledge_query` | Spoken biography summary |
| **Web Search**| *"Search for Python machine learning tutorials"* | `web_search` | Opens search query in default web browser |
| **Email** | *"Send an email to test@example.com saying hello"* | `send_email` | Dispatches TLS-encrypted SMTP email |
| **Email** | *"Send an email"* $\rightarrow$ *"test@example.com"* | `send_email` | Interactive multi-turn follow-up prompts |
| **Reminder** | *"Remind me to drink water in 30 minutes"* | `set_reminder` | Background timer set; speaks audible alert when done |
| **Reminder** | *"Remind me in 10 seconds"* | `set_reminder` | Asynchronous 10-second alert |
| **Custom** | *"Open YouTube"* | `custom_command` | Opens custom web URL |
| **Custom** | *"Who created you?"* | `custom_command` | Speaks custom response string |
| **System** | *"Exit"*, *"Quit"*, *"Goodbye"* | `exit` | Shuts down assistant cleanly |

---

## 🧩 Custom Commands System

Users can configure custom voice triggers without modifying Python code by editing [`config/custom_commands.json`](file:///e:/Projects/Voice%20Assistant/config/custom_commands.json).

### **JSON Schema Example**:
```json
{
  "commands": [
    {
      "name": "open youtube",
      "phrases": ["open youtube", "launch youtube"],
      "action_type": "open_url",
      "action_value": "https://www.youtube.com"
    },
    {
      "name": "who created you",
      "phrases": ["who created you", "who made you"],
      "action_type": "response",
      "action_value": "I was developed as an intelligent Python voice assistant."
    }
  ]
}
```

### **Supported Safe Actions**:
- `open_url`: Opens a whitelisted URL starting with `http://` or `https://`.
- `response`: Returns a predefined text response for TTS synthesis.
- **Security Policy**: Unsafe action types (`exec`, `eval`, `subprocess`) or `javascript:` schemes are **strictly rejected** by the custom command validator.

---

## ⏰ Timed Reminders System

- **Non-Blocking Architecture**: Reminders run in background daemon threads (`threading.Timer`) without freezing the main voice listener.
- **Natural Duration Units**: Supports seconds, minutes, hours, and phrases (*"an hour"*, *"a minute"*, *"10 sec"*, *"30 mins"*).
- **Audible Spoken Alerts**: Triggers pyttsx3 speech playback when the timer expires.
- **Concurrent Execution**: Handles multiple independent background timers simultaneously.

---

## ✉️ Voice Email Dispatch & Stateful Prompts

Nova supports complete or step-by-step voice email creation:

1. **Complete Single-Sentence Command**:
   > **User**: *"Send an email to test@example.com saying the meeting is at 5 PM."*  
   > **Nova**: *"Email sent successfully to test@example.com."*

2. **Interactive Multi-Turn Conversation**:
   > **User**: *"Send an email."*  
   > **Nova**: *"Who should I send it to?"*  
   > **User**: *"test@example.com"*  
   > **Nova**: *"What should the email say?"*  
   > **User**: *"Meeting is confirmed for 5 PM."*  
   > **Nova**: *"Email sent successfully to test@example.com."*

---

## 🌤️ Live Weather Lookup

- Queries OpenWeatherMap REST API `/data/2.5/weather`.
- Parses temperature (°C), feels-like temperature (°C), humidity (%), weather condition, and wind speed (m/s).
- Includes stateful prompt: If user asks *"What's the weather?"* without specifying a location, Nova prompts *"Which city would you like the weather for?"*.

---

## 📚 Wikipedia General Knowledge Q&A

- Queries Wikipedia REST API `/page/summary/{title}`.
- Strips question prefixes (*"what is"*, *"who was"*, *"explain"*, *"tell me about"*) to isolate target topics.
- Formats long articles into concise 1-2 sentence spoken summaries suitable for voice synthesis.

---

## 🛡️ Error Handling & Resiliency Safeguards

- **Microphone Timeouts**: Handled cleanly without throwing uncaught exceptions.
- **Unintelligible Speech**: Triggers a polite fallback message (*"I couldn't understand that. Please try again."*).
- **Missing Secrets**: Reports configuration status safely in logs and speaks friendly notices (*"The weather service is not configured yet."*).
- **Network Outages**: API errors (weather/knowledge/SMTP) return friendly messages (*"Unable to reach the service right now."*) without crashing Nova.

---

## 🔒 Privacy Policy & Data Processing

- **Microphone Audio**: Audio input is captured transiently in memory solely while listening for spoken commands. Audio buffers are **never stored on disk**.
- **Speech Decoding**: Spoken audio is decoded using Google's public Speech Recognition API over encrypted HTTPS.
- **External Services**: Weather queries are sent to OpenWeatherMap; general knowledge queries are sent to Wikipedia; emails are sent via your configured SMTP host.
- **Transient Memory**: Timed reminders exist only in active application memory.

---

## 🛡️ Security Safeguards

- **No Hardcoded Secrets**: All API tokens, usernames, and passwords reside in `.env`.
- **Git Exclusions**: `.env`, `logs/`, `__pycache__`, and `venv/` are protected by `.gitignore`.
- **Log Sanitization**: Passwords, tokens, and API keys are strictly redacted from log outputs.
- **No Unsafe Execution**: Arbitrary shell commands, `eval()`, `exec()`, or unsafe URL schemes are strictly prohibited.

---

## 🧪 Automated Testing & Verification

Nova includes a complete unit test suite using `unittest` and mocks:

```bash
python -m unittest discover tests
```

### **Test Suite Breakdown**:
- `test_foundation.py`: Phase 1 configuration defaults, date/time formatting, basic NLU.
- `test_phase2.py`: Phase 2 STT/TTS mocks, search query extraction, fallback handling.
- `test_phase3.py`: Phase 3 confidence thresholds, custom command security rejections.
- `test_phase4.py`: Phase 4 weather API mocks, knowledge Q&A, weather entity extraction.
- `test_phase5.py`: Phase 5 SMTP email mocks, duration parsing, background timer callbacks.
- `test_phase6.py`: Phase 6 security audit, credential redaction, logging, pipeline verification.

**Current Test Result**: **71 of 71 tests passed** (100% success rate).

---

## ❓ Troubleshooting Guide

| Symptom | Cause | Resolution |
| :--- | :--- | :--- |
| **"Microphone unavailable" warning** | PyAudio / mic device not detected | Connect microphone or select correct index in `.env` (`STT_MICROPHONE_INDEX`). |
| **"Weather service is not configured"** | Missing API key in `.env` | Add `OPENWEATHER_API_KEY` to `.env` file. |
| **"Email authentication failed"** | Incorrect SMTP credentials | Verify `EMAIL_USERNAME` and use a Google **App Password** instead of primary account password. |
| **Low NLU classification accuracy** | Non-standard phrase phrasing | Adjust `NLU_CONFIDENCE_THRESHOLD` in `config.py` or add training patterns to `intents.json`. |

---

## ⚠️ System Limitations

- **Internet Dependency**: Speech recognition, weather lookups, Wikipedia Q&A, and email delivery require an active internet connection.
- **Transient Reminders**: Active background reminders exist in thread memory and reset if Nova is restarted.
- **Gmail SMTP Requirements**: Gmail requires 2-Factor Authentication and an **App Password** for SMTP access.

---

## 🛣️ Future Roadmap

- **Persistent Reminder Database**: SQLite storage for recurring and persistent alarms across restarts.
- **Offline Local Speech Recognition**: Integration with lightweight offline STT engines (e.g. Vosk / Faster-Whisper).
- **Multi-Language Support**: Expanded NLU dictionaries and TTS voice selection for multiple languages.
- **GUI / Desktop Dashboard**: PySide / Electron desktop dashboard for visual assistant interaction.

---

## 📊 Project Status

**Current Status**: **COMPLETE & PRODUCTION-READY**

Nova has successfully completed all development phases (Phases 1–6). The project is fully tested, hardened against security vulnerabilities, documented, and suitable for technical portfolio demonstrations.
