<<<<<<< HEAD
# 🚀 FlowixPro: The Freelancer's "Clarity Engine"

**Transform messy client chaos into crystal-clear project plans in seconds.**

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 😫 The Problem
Every freelancer has been there: A client sends a 10-minute voice note, a chaotic WhatsApp message, or a vague email saying, *"I want a website like Amazon but simple and cheap."* 

This leads to:
- **Scope Creep**: Doing work you never agreed to.
- **Budget Mismatches**: Realizing too late that the client's budget is 1/10th of the actual cost.
- **Vague Requirements**: Losing days to back-and-forth emails.

## ✨ The Solution: FlowixPro
FlowixPro is a sophisticated AI orchestration engine that acts as your **Senior Project Manager**. It uses a multi-step "Expert Chain" to decode messy messages and deliver instant clarity.

### 🛠️ Killer Features
- **🔍 Specialized Analysis Modes**: 
    - **Summary**: Deciphers the client's actual intent.
    - **Scope**: Defines strict technical boundaries.
    - **Risks**: A ruthless audit of technical, budget, and timeline red flags.
    - **Gaps**: Highlights exactly what info you're missing before you can quote.
    - **Questions**: Generates strategic questions to win the deal.
- **🧠 Expert Chaining**: Uses specialized AI personas (Architect, Auditor, PM) for 3x higher accuracy than standard chatbots.
- **🛡️ Risk Mitigation**: Doesn't just find problems—it suggests professional strategies to handle them.

---

## 🏗️ How it Works (System Architecture)
FlowixPro isn't just a wrapper. It's a structured intelligence pipeline built on **Sequential Chaining**:

![System Architecture](system-architecture.png)

### The Intelligence Layers:
1.  **User Layer**: Capture the client's "chaos" and your analysis preference.
2.  **Intelligence Layer**: Employs **Sequential Expert Chaining**. The Architect decodes intent, the Auditor scans for risks, and the PM synthesizes the final professional plan.
3.  **Data Layer**: Uses **Pydantic Enforcement** to ensure the AI output is 100% reliable and structured.
=======
# 🚀 FlowixPro: The AI Project Clarity Engine

**Turn messy client messages into professional, structured project plans in seconds.**

FlowixPro is an AI-powered tool designed for freelancers and agencies who are tired of "scope creep" and vague client requirements. Whether it's a chaotic WhatsApp message, a rambling email, or a half-baked Upwork post, FlowixPro decodes the chaos and gives you instant clarity.

---

## ✨ Key Features
- **🎯 Multi-Mode Analysis**: Choose exactly what you want to extract:
  - **Summary**: Executive-level project goals.
  - **Scope**: Clear "In-Scope" vs. "Out-of-Scope" boundaries.
  - **Risks**: Ruthless audit of technical and financial red flags.
  - **Gaps**: Identification of missing info needed for quotes.
  - **Questions**: Strategic questions to send back to the client.
- **🧠 Multi-Step AI Pipeline**: Uses a chain of "AI Experts" (Architect, Auditor, and PM) for superior accuracy.
- **🛡️ Risk Mitigation**: Doesn't just find risks—it suggests professional mitigation strategies.
- **⚡ FastAPI Service**: Simple `/analyze` endpoint for product integration.


---

## 🏗️ System Architecture
FlowixPro runs as a **FastAPI** service and uses a 3-phase LangChain prompt flow:

```mermaid
graph TD
    A[Client Message] --> B[FastAPI: POST /analyze]
    B --> C[Phase 1: Architect (text)]
    C --> D[Phase 2: Auditor (text)]
    D --> E[Phase 3: Strategist (JSON)]
    E --> F[Validated JSON Output (Pydantic)]

    style B fill:#f9f9f9,stroke:#333,stroke-width:2px
    style C fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style D fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style E fill:#e1f5fe,stroke:#01579b,stroke-width:2px
    style F fill:#f1f8e9,stroke:#33691e,stroke-width:2px
```
>>>>>>> main

---

## 🛠️ Technology Stack
<<<<<<< HEAD
- **Core Intelligence**: OpenAI GPT-4o-mini
- **Orchestration**: LangChain / LlamaIndex
- **UI Framework**: Gradio / Streamlit
- **Reliability**: Pydantic V2 (Strict Type Enforcement)

---

## 🚀 Quick Start

### 1. Installation
```bash
git clone https://github.com/iammawaistariq/Freelancer-Clarity-Engine.git
cd Freelancer-Clarity-Engine
pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file and add your OpenAI API Key:
```env
OPENAI_API_KEY=your_api_key_here
```

### 3. Run
```bash
python app.py
```

---
*Built to help freelancers respond faster, avoid confusion, and never lose a deal to unclear requirements again.*
=======
- **LLM**: OpenAI `gpt-4o-mini` (default) or Groq-hosted Llama models
- **Orchestration**: LangChain (`ChatOpenAI` + `ChatPromptTemplate`)
- **API**: FastAPI + Uvicorn
- **Data Validation**: Pydantic V2
- **Environment**: Python 3.9+

---

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/your-username/FlowixPro.git
cd FlowixPro
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Environment Variables
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_api_key_here
# optional (only if using Groq)
GROQ_API_KEY=your_groq_key_here

# defaults shown in Swagger
FLOWIX_PROVIDER=openai
FLOWIX_MODEL=gpt-4o-mini
FLOWIX_TEMPERATURE=0.1
```

### 4. Run the application
```bash
uvicorn main:app --reload
```

### 5. Use the API

- Health: `GET /health`
- Defaults: `GET /defaults`
- Analyze: `POST /analyze`

Example request:

```json
{
  "message": "Need an ecommerce site in 2 weeks with $200 budget"
}
```

---

>>>>>>> main
