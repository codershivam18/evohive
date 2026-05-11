import gradio as gr
import time
import plotly.graph_objects as go
from evolution.genetic_prompt import EvolutionEngine
from agents.hive import AgentHive
from utils import save_best_prompt
from config import config

# Premium Laboratory CSS
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=JetBrains+Mono&display=swap');

:root {
    --primary: #6366f1;
    --secondary: #a855f7;
    --bg: #0f172a;
    --card-bg: rgba(30, 41, 59, 0.7);
}

body { background-color: var(--bg) !important; font-family: 'Outfit', sans-serif !important; }
.gradio-container { max-width: 1200px !important; }

/* Glassmorphism Effect */
.glass-panel {
    background: var(--card-bg) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

h1 { 
    background: linear-gradient(90deg, #6366f1, #a855f7);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 600 !important;
    font-size: 2.5rem !important;
    margin-bottom: 0.5rem !important;
}

.status-badge {
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
}

.status-online { background: #10b981; color: white; }

/* Custom Chatbot Styling */
.chatbot-container { border-radius: 12px !important; overflow: hidden !important; }

button.primary {
    background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
    border: none !important;
    transition: transform 0.2s !important;
}

button.primary:hover { transform: translateY(-2px); box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4); }
"""

def create_fitness_plot(history):
    if not history: return None
    fig = go.Figure()
    gens = [h['gen'] for h in history]
    bests = [h['best'] for h in history]
    avgs = [h['avg'] for h in history]
    
    fig.add_trace(go.Scatter(x=gens, y=bests, mode='lines+markers', name='Best Fitness', line=dict(color='#6366f1', width=3)))
    fig.add_trace(go.Scatter(x=gens, y=avgs, mode='lines', name='Avg Fitness', line=dict(color='#a855f7', dash='dot')))
    
    fig.update_layout(
        title="🧬 Evolutionary Trajectory",
        xaxis_title="Generation",
        yaxis_title="Fitness Score",
        template="plotly_dark",
        margin=dict(l=20, r=20, t=40, b=20),
        height=350,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def solve_task(task: str, skip_evo: bool, pop_size: int, num_gens: int):
    if not task.strip():
        yield [], "Please enter a task.", None
        return

    chat_history = [{"role": "assistant", "content": "🚀 Initializing EvoHive Laboratory..."}]
    yield chat_history, "", None
    
    best_prompt = None
    fig = None

    if not skip_evo:
        chat_history.append({"role": "assistant", "content": f"🧬 Starting Evolution (Pop: {pop_size}, Gens: {num_gens})..."})
        yield chat_history, "", None
        
        # Override config temporarily for this run
        config.POPULATION_SIZE = pop_size
        config.NUM_GENERATIONS = num_gens
        
        engine = EvolutionEngine(task)
        
        def on_gen_complete(gen, b_prompt, score):
            chat_history.append({"role": "assistant", "content": f"🧬 **Evolution**: Generation {gen+1} complete. Best Score: **{score:.2f}**"})

        # Run Evolution (Parallelized in the engine now)
        best_prompt, history = engine.run_evolution(callback=on_gen_complete)
        save_best_prompt(f"evolved_{int(time.time())}", best_prompt, history[-1]['best'] if history else 0.0)
        fig = create_fitness_plot(history)
        chat_history.append({"role": "assistant", "content": "✅ Evolution finished. Optimal prompt identified."})
        yield chat_history, "", fig
    
    chat_history.append({"role": "assistant", "content": "🐝 Activating Agent Hive..."})
    yield chat_history, "", fig
    
    hive = AgentHive()
    hive_gen = hive.run_task(task, system_prompt=best_prompt)
    
    final_result = ""
    for step in hive_gen:
        if isinstance(step, str) and (step.startswith("🔍") or step.startswith("✅") or step.startswith("💻") or step.startswith("🧐") or step.startswith("🛠️") or step.startswith("🧠")):
            chat_history.append({"role": "assistant", "content": f"🐝 **Hive**: {step}"})
            yield chat_history, "", fig
        else:
            # Final result
            final_result = step
    
    chat_history.append({"role": "assistant", "content": "✨ Mission Accomplished."})
    yield chat_history, final_result, fig

with gr.Blocks() as interface:
    with gr.Row():
        with gr.Column(scale=8):
            gr.Markdown(f"# {config.APP_TITLE}")
            gr.Markdown("#### Autonomous Multi-Agent Evolution & Problem Solving")
        with gr.Column(scale=2):
            gr.HTML('<div style="text-align: right; margin-top: 20px;"><span class="status-badge status-online">● Hive Online</span></div>')

    with gr.Row(elem_classes=["glass-panel"]):
        with gr.Column(scale=1):
            gr.Markdown("### 🎯 Mission Brief")
            task_input = gr.Textbox(
                label="Objective", 
                placeholder="What should the Hive solve today?", 
                lines=5,
                elem_id="task-input"
            )
            
            with gr.Accordion("🧬 Evolution Protocol", open=True):
                skip_evo_check = gr.Checkbox(label="⚡ Direct Solve (Skip Evolution)", value=False)
                pop_slider = gr.Slider(label="Population Size", minimum=4, maximum=20, step=2, value=config.POPULATION_SIZE)
                gen_slider = gr.Slider(label="Generations", minimum=1, maximum=10, step=1, value=config.NUM_GENERATIONS)
            
            run_btn = gr.Button("🚀 START MISSION", variant="primary", elem_id="run-btn")
            
        with gr.Column(scale=2):
            with gr.Tabs():
                with gr.TabItem("📊 Mission Control"):
                    status_chat = gr.Chatbot(
                        label="Live Laboratory Feed", 
                        height=450,
                        elem_classes=["chatbot-container"]
                    )
                with gr.TabItem("🧬 Genetic Analysis"):
                    output_plot = gr.Plot(label="Evolution Progress")
                    
                with gr.TabItem("📝 Final Intelligence"):
                    final_output = gr.Markdown("### The results of the Hive's synthesis will appear here.")

    run_btn.click(
        fn=solve_task,
        inputs=[task_input, skip_evo_check, pop_slider, gen_slider],
        outputs=[status_chat, final_output, output_plot]
    )

if __name__ == "__main__":
    interface.launch(
        server_name="127.0.0.1", 
        server_port=7860, 
        share=False,
        css=custom_css,
        theme=gr.themes.Default()
    )