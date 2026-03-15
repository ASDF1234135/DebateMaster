# DebateMaster
> **Where Perspectives Collide and Insights Emerge.**

![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Vue.js](https://img.shields.io/badge/vuejs-%2335495e.svg?style=for-the-badge&logo=vuedotjs&logoColor=%234FC08D)
![PostgreSQL](https://img.shields.io/badge/postgresql-4169e1?style=for-the-badge&logo=postgresql&logoColor=white)

## What is DebateMaster?

**DebateMaster** is an intelligent, multi-agent debate platform powered by Large Language Models (LLMs) and LangGraph. It is designed to help users break out of echo chambers, rigorously analyze complex topics, and make well-rounded decisions through automated AI-driven debates.

Instead of receiving a single, potentially biased answer from a standard AI, DebateMaster allows you to define a specific **Topic**, upload background **Context**, and set up distinct **Personas**. The system then orchestrates a structured debate:
1. **Affirmative Agent (Pro):** Defends the core argument based on its assigned persona.
2. **Negative Agent (Con):** Actively challenges the affirmative side, finding loopholes and counterarguments.
3. **Objective Judge:** Synthesizes the entire debate history, evaluates the strengths and weaknesses of both sides, and provides a comprehensive final report with actionable improvement tips.

---

## How to Deploy

DebateMaster is fully containerized. Deploying the entire stack (Frontend, Backend, and Database) takes only a few minutes using Docker Compose.

### Prerequisites
* [Docker](https://www.docker.com/get-started) and Docker Compose installed on your machine.
* An OpenAI API Key (We ONLY support OpenAI-Compatible Models).

### Deployment Steps

**1. Clone the repository**
```bash
git clone https://github.com/ASDF1234135/DebateMaster.git
cd DebateMaster
```

**2. Set up the environment variables**
```bash
# Database Configuration
POSTGRES_USER=my_db_user
POSTGRES_PASSWORD=my_super_secret_password
POSTGRES_DB=debate_db

# AI Engine Configuration
OPENAI_API_KEY=your-openai-api-key-here
```

**3. Build and run the containers**
```bash
docker-compose up -d --build
```
It will start 3 docker containers: frontend, backend and DB

**4. Access the application**
Once the containers are successfully started, you can access the platform at:
* Frontend Web Interface: http://localhost
* Backend API Docs (Swagger UI): http://localhost:8000/docs