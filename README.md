# 🇸🇦 Saudi Mostadam Agent (نظام مستدام السعودية)

An AI-powered energy management, sustainability analytics, and regulatory compliance agent designed for Saudi enterprises, aligned with the Saudi Building Code (SBC) and Vision 2030.

---

## 📌 Project Overview
**Saudi Mostadam Agent** is an intelligent, scalable software system that serves as a digital consultant for facility management. It leverages Data Science, Machine Learning, and Generative AI to automate sustainability audits, predict building compliance, and provide localized, actionable engineering recommendations to reduce carbon footprints and optimize energy efficiency.

### ⚠️ The Problem
Modern facility management sectors face significant gaps, including unmonitored energy waste leading to high carbon emissions, and slow, error-prone manual compliance checking. Existing tools only report violations after they occur, lacking proactive guidance to fix them.

### 💡 The Solution
The system provides a robust, fault-tolerant centralized environment based on four main technical pillars:
1. **Interactive Analytics Dashboard:** Built to process large-scale consumption data and display instant KPIs and real-time trends.
2. **Predictive Compliance Engine:** A Machine Learning framework (Classification & Regression) that forecasts future compliance status based on building parameters (area, type, expected load) to avoid penalties proactively.
3. **Interactive AI Agent:** A Generative AI LLM consultant tailored with custom system instructions, fully capable of understanding Arabic and local dialects, providing instant, concise engineering advice based on the building's historical data.
4. **Automated Reporting System:** Generates comprehensive, exportable compliance reports tailored for executive stakeholders.

---

## 📂 Project Structure

```text
Saudi-Mostadam-Agent/
│
├── .gitignore               # Files and directories ignored by Git (e.g., .venv, __pycache__)
├── LICENSE                  # Project License (MIT)
├── README.md                # Project documentation and guide (This file)
├── requirements.txt         # Required python libraries and packages
│
├── data/                    # Data storage
│   ├── raw/                 # Unprocessed consumption data
│   └── processed/           # Cleaned data ready for ML training
│
├── models/                  # Predictive compliance models
│   ├── train_model.py       # Script used for training the ML model
│   └── compliance_model.pkl # Trained and serialized model ready for inference
│
├── src/                     # Source code core logic
│   ├── __init__.py          # Makes the folder a Python module
│   ├── agent.py             # GenAI LLM Agent and specialized system prompts
│   ├── predictor.py         # Compliance prediction inference handler
│   └── utils.py             # Utility functions (CO2 calculation, text processing)
│
└── app.py                   # Main entry point for the Streamlit interactive UI