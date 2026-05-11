from utils import get_llm
from memory.vector_store import MemoryStore
from config import config

class AgentHive:
    def __init__(self):
        self.memory = MemoryStore()
        self.agents = {
            "researcher": "You are a thorough researcher. Gather facts and ideas.",
            "critic": "You are a strict critic. Find flaws and risks.",
            "coder": "You are an expert Python developer. Write clean, efficient code.",
            "synthesizer": "You combine all inputs into a final high-quality answer."
        }

    def run_task(self, task: str, system_prompt: str = None):
        """Runs the Hive with an optional evolved system prompt. Yields status updates and final result."""
        responses = {}
        llm = get_llm()
        
        # 1. Research Phase
        yield "🔍 **Researcher** is gathering data and facts..."
        res_prompt = f"{system_prompt or self.agents['researcher']}\n\nTask: {task}"
        responses['researcher'] = llm.invoke(res_prompt)
        yield "✅ Research complete."

        # 2. Iterative Code/Critique Loop
        yield "💻 **Coder** is generating the initial solution..."
        code_prompt = f"{system_prompt or self.agents['coder']}\n\nContext: {responses['researcher']}\nTask: {task}"
        coder_output = llm.invoke(code_prompt)
        
        yield "🧐 **Critic** is reviewing the output for flaws..."
        critic_prompt = f"{self.agents['critic']}\n\nOriginal Task: {task}\nProduced Work: {coder_output}"
        critic_feedback = llm.invoke(critic_prompt)
        
        if "FIX" in critic_feedback.upper() or "IMPROVE" in critic_feedback.upper():
            yield "🛠️ **Hive** detected flaws. Refining solution based on critique..."
            coder_output = llm.invoke(f"{code_prompt}\n\nFeedback from Critic: {critic_feedback}")
            yield "✅ Refinement complete."

        responses['coder'] = coder_output
        responses['critic'] = critic_feedback

        # 3. Final Synthesis
        yield "🧠 **Synthesizer** is assembling the final answer..."
        final_prompt = f"Synthesize a final high-quality answer.\nContext: {responses['researcher']}\nCritic Feedback: {responses['critic']}\nFinal Work: {responses['coder']}"
        final_result = llm.invoke(final_prompt)
        
        yield final_result