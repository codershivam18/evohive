# 🧬 EvoHive AI Laboratory

**EvoHive** is a self-improving, multi-agent AI laboratory optimized for local execution on NVIDIA hardware (RTX 3050+). It combines **Genetic Algorithms** with a **Multi-Agent Hive** to autonomously evolve, critique, and solve complex tasks.

![EvoHive UI](https://img.shields.io/badge/UI-Gradio_6.0-indigo)
![Engine](https://img.shields.io/badge/Engine-Genetic_Evolution-purple)
![LLM](https://img.shields.io/badge/Local_LLM-Ollama-orange)
[![Live Demo](https://img.shields.io/badge/Live_Demo-EvoHive_Lab-FF3366?style=for-the-badge&logo=rocket)](https://ef6b54c4a8d6d3683e.gradio.live)

---

## 🚀 Key Features

- **🧬 Genetic Prompt Evolution**: Autonomously evolves system prompts through selection, crossover, and mutation to find the perfect instructions for any task.
- **🐝 Multi-Agent Hive**: A collaborative swarm of specialized agents (Researcher, Coder, Critic, Synthesizer) that work in an iterative loop to refine solutions.
- **⚡ Parallel Evaluation**: Population fitness is calculated concurrently, maximizing local GPU/CPU throughput.
- **🧠 Evaluation Caching**: Remembers previously judged prompts to skip redundant LLM calls and accelerate later generations.
- **💎 Premium Dashboard**: A glassmorphism-inspired UI with live progress feeds, evolutionary trajectory plots, and real-time agent logs.
- **🐳 Docker Ready**: Includes `docker-compose` for one-click deployment with full NVIDIA GPU support.

## 🛠️ Installation

1. **Prerequisites**:
   - Install [Ollama](https://ollama.com/) and pull models: `ollama pull llama3.2:3b`.
   - Python 3.10+

2. **Setup**:
   ```bash
   pip install -r requirement.txt
   ```

3. **Launch**:
   ```bash
   python main.py
   ```

## 🧪 How it Works

1. **Evolution Phase**: The system creates a population of diverse system prompts.
2. **Judging Phase**: A specialized "Judge AI" evaluates each prompt's performance based on Clarity, Strategy, and Precision.
3. **Hive Phase**: The best-evolved prompt is handed to the Hive Agents, who research, code, and critique the final solution.

## 📦 Deployment

Deploy to your local network or a GPU VPS using Docker:
```bash
docker-compose up -d --build
```

---

## 📜 License
MIT License. Created by [codershivam18](https://github.com/codershivam18).
