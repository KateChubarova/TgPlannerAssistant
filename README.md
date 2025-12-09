<p align="right">
  <img src="https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white" alt="Python version">
  <img src="https://img.shields.io/badge/FastAPI-0.109%2B-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Docker%20Compose-v2%2B-2496ED?logo=docker&logoColor=white" alt="Docker Compose">
  <img src="https://img.shields.io/badge/RAG-enabled-purple?logo=openai&logoColor=white" alt="RAG">
  <img src="https://img.shields.io/badge/OpenAI-API-brightgreen?logo=openai&logoColor=white" alt="OpenAI API">

  <!-- Google Calendar -->
  <img src="https://img.shields.io/badge/Google%20Calendar-integrated-34A853?logo=googlecalendar&logoColor=white" alt="Google Calendar">

  <!-- Google Web Search -->
  <img src="https://img.shields.io/badge/Google%20Search-enabled-4285F4?logo=google&logoColor=white" alt="Google Web Search">
</p>

# Tg-Planner-Assistant
🔗 **https://t.me/chubakaGPT_bot**

Tg-Planner-Assistant is a Telegram-based assistant that uses a Retrieval-Augmented Generation (RAG) pipeline and a FastAPI backend to process user requests, generate responses, and manage embeddings.
The project includes server components, shared utilities, migration tooling, and deployment configuration using Docker.

---

## 📂 Project Structure
````
├── .github/ # GitHub Actions workflows (CI/CD)
├── .idea/ # IDE configuration (PyCharm/IntelliJ)
├── .venv/ # Local Python virtual environment (ignored)
│
├── migrations/ # Alembic migration scripts
│
├── src/
│ ├── client/ # Telegram bot client logic
│ ├── rag/ # RAG pipeline: embeddings, retrieval logic
│ ├── server/ # FastAPI server modules, endpoints, services
│ ├── shared/ # Shared Python modules used across src
│ └── sources/ # Integrations with external services
│ ├── web_search.py # Web search integration
│ ├── google_calendar.py # Google Calendar API integration
│ └── init.py
│
├── .dockerignore
├── .env # Environment variables (not committed)
├── .gitignore # Git ignore rules (excluded files & folders)
├── .pre-commit-config.yaml # Pre-commit hooks configuration
│
├── alembic.ini # Alembic configuration
├── compose.yaml # Docker Compose configuration
│
├── Dockerfile # Builds backend container
│
├── credentials.json # (private) Application credentials
├── web_credentials.json # (private) Google API credentials
├── deploy_key # SSH deployment key
├── deploy_key.pub
├── gha_deploy_key # GitHub Actions deploy key
├── gha_deploy_key.pub
│
├── README.Docker.md # Additional Docker instructions
├── README.md # Main project documentation
│
└── requirements.txt # Python dependencies
````

---

## 🚀 Setup & Run

The recommended way to run the project is via **Docker Compose**.

---

### **1️⃣ Send your Google email**

Send the **Google email address that has an active Google Calendar** to one of the following contacts:

- 📧 **katsiaryna.chubarava@innowise.com**
- 💬 Telegram: **@k_chubaka**

This email is required to grant access to Google Calendar and complete the integration setup.

---

### **2️⃣ Prerequisites**

- **Docker**
- **Docker Compose v2+** (or Docker Desktop)
- **Python 3.12**

---

### **3️⃣ Clone the repository**

```bash
git clone https://github.com/katsiarynach/Tg-Planner-Assistant.git Tg-Planner-Assistant
cd Tg-Planner-Assistant
```

### **4️⃣ Configure environment**

```env
# Create .env in the project root (next to compose.yaml)
# and define all environment variables that the app expects.

TELEGRAM_BOT_TOKEN=
    Telegram Bot API token used to connect the assistant to your bot.
    Must be generated via BotFather.

OPENAI_API_KEY=
    API key for OpenAI models (chat model + embeddings).
    Required for conversation generation and RAG embeddings.

DATABASE_URL=
    SQLAlchemy-compatible URL for connecting to PostgreSQL inside Docker.
    Example: postgresql://<user>:<password>@db:5432/<database>

POSTGRES_USER=
    PostgreSQL username used inside the database container.

POSTGRES_PASSWORD=
    PostgreSQL password used inside the database container.

POSTGRES_DB=
    Name of the PostgreSQL database created by Docker.

REDIRECT_URI=
    OAuth redirect URL for Google Calendar authorization.
    Must match the URL added in Google Cloud Console.

EMBEDDING_MODEL=
    Name of the OpenAI embedding model used for vector generation.
    Example: text-embedding-3-small

CHAT_MODEL=
    Chat model used for generating responses.
    Example: gpt-4o-mini

WEB_GOOGLE_CREDENTIALS=
    Path inside the Docker container where OAuth credentials are mounted.
    Example: /app/web_credentials.json

GOOGLE_CREDENTIALS=
    Path to the Google service account credentials used by backend.
    Example: /app/credentials.json

GOOGLE_SEARCH_API_KEY=
    API key for Google Custom Search JSON API.

GOOGLE_SEARCH_CX=
    Google Custom Search "CX" (search engine ID).
    Defines which custom search engine to query.

GOOGLE_SEARCH_URL=
    Base URL of the Google Custom Search API.
    Usually: https://www.googleapis.com/customsearch/v1
```

````
# Place credentials files for Google APIs (Calendar & Web Search)
# in the project root:

credentials.json      # Backend / service account credentials
web_credentials.json  # OAuth client credentials
````
### **5️⃣ Build and run with Docker**

```bash
# From the project root:
docker compose up --build

# This will:
# - Build the Docker image using the Dockerfile
# - Install all Python dependencies from requirements.txt inside the image
# - Start all services defined in compose.yaml
#   (FastAPI backend, Telegram bot, database, etc.)
# - Load environment variables from .env

# To stop the stack:
docker compose down
```
