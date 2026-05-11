import gradio as gr
import time
import plotly.graph_objects as go
from evolution.genetic_prompt import EvolutionEngine
from agents.hive import AgentHive
from utils import save_best_prompt
from config import config

# Strater-Inspired Premium CSS
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;800&family=JetBrains+Mono&display=swap');

:root {
    --primary: #FF3366; /* Strater Pink */
    --secondary: #38BDF8; /* Sky Blue */
    --bg: #FFFFFF;
    --grid-color: #f1f1f1;
    --text-main: #0F172A;
    --text-muted: #64748B;
    --card-bg: #FFFFFF;
}

body { 
    background-color: var(--bg) !important; 
    background-image: radial-gradient(var(--grid-color) 1px, transparent 1px);
    background-size: 30px 30px;
    font-family: 'Plus Jakarta Sans', sans-serif !important; 
    color: var(--text-main) !important;
}

.gradio-container { 
    max-width: 1300px !important; 
    width: 95% !important;
}

/* Bento-Box Style */
.glass-panel {
    background: var(--card-bg) !important;
    border: 1.5px solid #E2E8F0 !important;
    border-radius: 32px !important;
    padding: 30px !important;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05) !important;
    margin-bottom: 24px !important;
}

h1 { 
    color: var(--text-main) !important;
    font-weight: 800 !important;
    font-size: clamp(2rem, 6vw, 3.5rem) !important;
    letter-spacing: -0.04em !important;
    margin-bottom: 0.5rem !important;
}

h4 {
    color: var(--text-muted) !important;
    font-weight: 500 !important;
    font-size: 1.1rem !important;
}

.status-badge {
    padding: 8px 16px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border: 1px solid #E2E8F0;
    background: white;
}

.status-online::before {
    content: "";
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #FF3366;
    border-radius: 50%;
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0% { box-shadow: 0 0 0 0 rgba(255, 51, 102, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(255, 51, 102, 0); }
    100% { box-shadow: 0 0 0 0 rgba(255, 51, 102, 0); }
}

/* Custom Chatbot Styling */
.chatbot-container { 
    border: 1px solid #E2E8F0 !important;
    border-radius: 20px !important; 
    background: #F8FAFC !important;
}

button.primary {
    background: var(--text-main) !important; /* High contrast black buttons like Strater */
    color: white !important;
    border-radius: 100px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: none !important;
}

button.primary:hover { 
    background: var(--primary) !important;
    transform: translateY(-2px);
    box-shadow: 0 12px 20px -8px rgba(255, 51, 102, 0.5);
}

/* Accordion Styling */
.gr-accordion {
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    overflow: hidden;
}
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
        with gr.Column(scale=10):
            gr.Markdown(f"# {config.APP_TITLE}")
            gr.Markdown("#### Autonomous Multi-Agent Evolution & Problem Solving")
        with gr.Column(scale=2, min_width=150):
            gr.HTML('<div style="text-align: right;"><span class="status-badge status-online">● Hive Online</span></div>')

    with gr.Row(elem_classes=["glass-panel"]):
        with gr.Column(scale=1, min_width=320):
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
            
        with gr.Column(scale=2, min_width=320):
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
        server_name="0.0.0.0", 
        server_port=7860, 
        share=True,
        css=custom_css,
        theme=gr.themes.Default()
    )