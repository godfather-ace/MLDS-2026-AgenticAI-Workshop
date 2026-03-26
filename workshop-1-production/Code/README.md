# 🤖 Locally Deployed AI Research Agent

A multi-agent AI research assistant built with **OpenAI Agents SDK** and **Streamlit**, containerised with Docker and deployed to AWS ECS via **AWS Copilot**.

The app routes user queries to specialist agents (Physics or Financial research) using a triage agent with an input guardrail to ensure only research-related questions are processed.

---

## 🏗️ Architecture

```
User Query
    │
    ▼
┌─────────────────────────────┐
│        Triage Agent         │
│  (with Input Guardrail)     │
└────────────┬────────────────┘
             │
     ┌───────┴────────┐
     ▼                ▼
┌─────────┐    ┌───────────┐
│ Physics │    │ Financial │
│ Agent   │    │ Agent     │
└─────────┘    └───────────┘
```

- **Guardrail Agent** — validates that the query is research-related before it reaches the triage agent
- **Triage Agent** — routes the validated query to the appropriate specialist
- **Physics Research Agent** — handles physics-domain queries with step-by-step reasoning
- **Financial Research Agent** — handles finance-domain queries with contextual explanations

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | [Streamlit](https://streamlit.io/) |
| Agent Framework | [OpenAI Agents SDK](https://github.com/openai/openai-agents-python) |
| Data Validation | [Pydantic](https://docs.pydantic.dev/) |
| Container | Docker (Python 3.11 slim) |
| Deployment | AWS ECS via [AWS Copilot](https://aws.github.io/copilot-cli/) |
| Load Balancer | AWS Application Load Balancer |

---

## 📁 Project Structure

```
.
├── app.py               # Main Streamlit app & agent definitions
├── requirements.txt     # Python dependencies
├── Dockerfile           # Container build instructions
└── copilot/
    ├── ragagentservice/
    │   └── manifest.yml # Copilot Load Balanced Web Service manifest
    └── environments/
        └── prod/
            └── manifest.yml # Copilot prod environment manifest
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Docker
- AWS CLI configured with appropriate permissions
- [AWS Copilot CLI](https://aws.github.io/copilot-cli/docs/overview/) installed
- An OpenAI API key

### Run Locally

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd <repo-name>
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

4. Open your browser at `http://localhost:8501`, enter your OpenAI API key in the sidebar, and submit a research query.

### Run with Docker

```bash
docker build -t ai-research-agent .
docker run -p 8501:8501 ai-research-agent
```

Then visit `http://localhost:8501`.

---

## ☁️ Deploy to AWS with Copilot

This project uses AWS Copilot to deploy a **Load Balanced Web Service** on ECS Fargate.

### 1. Initialise the Copilot application (first time only)

```bash
copilot app init
```

### 2. Create the production environment

```bash
copilot env deploy --name prod
```

### 3. Deploy the service

```bash
copilot svc deploy --name ragagentservice --env prod
```

Copilot will build the Docker image, push it to ECR, and deploy it behind an Application Load Balancer. The public URL will be printed on completion.

### Service Configuration

The service is configured in `copilot/ragagentservice/manifest.yml`:

| Setting | Value |
|---|---|
| Type | Load Balanced Web Service |
| Port | 8501 |
| CPU | 256 units |
| Memory | 512 MiB |
| Tasks | 1 |
| Platform | linux/x86_64 |

---

## 📦 Dependencies

```
pydantic-ai
openai-agents
nest-asyncio
streamlit
```

---

## 🛡️ Guardrail Behaviour

The input guardrail uses a dedicated `GuardrailAgent` to classify every query before it reaches the triage agent. If the query is **not** research-related, the tripwire is triggered and the query is rejected — preventing misuse of the specialist agents.

---
