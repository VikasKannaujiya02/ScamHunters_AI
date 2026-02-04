# 🕵️‍♂️ ScamHunters AI - Agentic Honeypot System

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/Framework-FastAPI-009688)
![AI](https://img.shields.io/badge/AI-Gemini%20Pro-orange)
![Deployment](https://img.shields.io/badge/Deployment-Render-purple)
![Status](https://img.shields.io/badge/Status-Live-success)

## 📜 Project Overview
**ScamHunters AI** is an advanced **Agentic Honeypot** designed to actively defend against digital fraud. Instead of simply blocking spam, this system intercepts scam messages and deploys an autonomous AI Agent to engage the scammer.

The system mimics a naive, non-tech-savvy elderly victim (Persona: *"Savitri Devi"*), engages the scammer in multi-turn conversations to waste their time, and stealthily extracts forensic intelligence (UPI IDs, Bank Accounts, Location) to report to authorities.

---

## 🚀 Key Features

### 🤖 1. Autonomous AI Persona
- **Persona:** "Savitri Devi" - An elderly, confused, but wealthy victim.
- **Dynamic Response:** Uses **Google Gemini Pro** to generate context-aware, human-like replies.
- **Sentiment Analysis:** Detects urgency or aggression in scammer messages and adapts tone.

### 🎣 2. Digital Forensics & Traps
- **Voice Trap:** Generates realistic **AI Voice Notes** using text-to-speech to convince scammers they are talking to a real human.
- **Payment Trap:** Auto-generates **Fake UPI Payment Screenshots** (e.g., "₹5,000 sent") to confuse scammers and prolong the session.

### 🔍 3. Intelligence Extraction
- Automatically parses chat logs to extract:
  - 📞 Phone Numbers
  - 💸 UPI IDs & Bank Account Numbers
  - 🔗 Phishing Links
  - 📍 Geo-Location & IP Metadata

### 📡 4. Mandatory Compliance Reporting
- **Real-time Callback:** As per Hackathon Rule 12, extracted intelligence is instantly sent to the **GUVI Central Evaluation Node**.

---

## ⚙️ System Architecture & Workflow

1.  **Intercept:** Incoming JSON request received via API.
2.  **Process:** AI analyzes intent and generates a conversational reply.
3.  **Trap:** If specific keywords ("pay", "call") are detected, traps (Image/Audio) are generated.
4.  **Respond:** Immediate response sent to the scammer (Low Latency).
5.  **Report:** Background task sends forensic data to the Central Node.

---

## 🛠️ Tech Stack

| Component | Technology Used |
| :--- | :--- |
| **Backend Framework** | FastAPI (Python) |
| **AI Engine** | Google Gemini Generative AI |
| **Forensics** | Pillow (Image Proc), gTTS (Voice), Regex |
| **Deployment** | Render Cloud |
| **Task Management** | Asyncio & BackgroundTasks |
| **Database** | Excel/Pandas (Local Logging) |

---

## 🔌 API Documentation

**Base URL:** `https://scamhunters-api.onrender.com`

### 🔹 1. Chat Endpoint (Main Honeypot)
This endpoint handles incoming scam messages and returns the AI response.

- **URL:** `/api/chat`
- **Method:** `POST`
- **Auth:** `x-api-key: 12345`

#### **Request Format (JSON):**
```json
{
  "sessionId": "session_12345",
  "message": {
    "sender": "scammer",
    "text": "Your account is blocked. Pay Rs 5000 immediately.",
    "timestamp": 1770005528731
  },
  "conversationHistory": []
}
