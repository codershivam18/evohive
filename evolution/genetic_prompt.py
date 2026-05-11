import random
import time
import threading
from deap import base, creator, tools
from config import config
from utils import get_fast_llm, call_ollama, get_llm

# Setup DEAP
if not hasattr(creator, "FitnessMax"):
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMax)

class EvolutionEngine:
    def __init__(self, task: str):
        self.task = task
        self.toolbox = base.Toolbox()
        self.toolbox.register("individual", self.init_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self.evaluate_prompt)
        self.toolbox.register("mate", self.crossover)
        self.toolbox.register("mutate", self.mutate)
        self.toolbox.register("select", tools.selBest)
        
        # Performance Cache to skip redundant evaluations
        self.fitness_cache = {}
        self.cache_lock = threading.Lock()

    def init_individual(self):
        base_prompts = [
            "You are an expert assistant. Solve the task concisely.",
            "You are a detailed AI researcher. Think step-by-step and provide facts.",
            "You are a creative problem solver. Use analogies and clear examples.",
            "You are a master coder. Focus on efficiency and best practices."
        ]
        prompt = random.choice(base_prompts)
        return creator.Individual([prompt])

    def mutate(self, individual):
        if random.random() < config.MUTATION_RATE:
            original_prompt = individual[0]
            mutation_strategies = [
                "Make it more authoritative.",
                "Add a requirement to think step-by-step.",
                "Encourage the use of metaphors.",
                "Tell it to be extremely critical of its own first thoughts.",
                "Add a constraint to be concise and use bullet points."
            ]
            strategy = random.choice(mutation_strategies)
            mutation_prompt = f"Improve the following system prompt based on this strategy: {strategy}\nOriginal Prompt: {original_prompt}\nReturn ONLY the new improved prompt text."
            try:
                new_prompt = call_ollama(mutation_prompt, model=config.FAST_MODEL)
                individual[0] = new_prompt.strip()
            except:
                pass
        return (individual,)

    def crossover(self, ind1, ind2):
        synthesis_prompt = f"Combine the best elements of these two system prompts into one superior prompt.\nPrompt A: {ind1[0]}\nPrompt B: {ind2[0]}\nReturn ONLY the combined superior prompt text."
        try:
            combined = call_ollama(synthesis_prompt, model=config.FAST_MODEL)
            ind1[0] = combined.strip()
        except:
            pass
        return ind1, ind2

    def evaluate_prompt(self, individual):
        prompt = individual[0]
        
        # Check cache first (Speed boost)
        with self.cache_lock:
            if prompt in self.fitness_cache:
                return (self.fitness_cache[prompt],)

        try:
            test_llm = get_llm(temperature=0.7)
            response = test_llm.invoke(f"System: {prompt}\n\nUser Task: {self.task}")
            
            # Stronger Multi-Criteria Judge
            judge_prompt = f"""Rate this AI response for the mission: "{self.task}"
            
            Response to Evaluate: {response[:1200]}
            
            Evaluate based on:
            1. Clarity & Structure
            2. Strategic Depth
            3. Precision of Facts
            
            Return ONLY a single numerical score between 0.0 and 1.0 (e.g., 0.85). 
            Do not explain. Just the number."""
            
            score_text = call_ollama(judge_prompt, model=config.FAST_MODEL)
            import re
            numbers = re.findall(r"[-+]?\d*\.\d+|\d+", score_text)
            score = float(numbers[0]) if numbers else 0.5
            final_score = max(0.0, min(1.0, score))
            
            # Save to cache
            with self.cache_lock:
                self.fitness_cache[prompt] = final_score
                
            return (final_score,)
        except Exception as e:
            return (0.4,)

    def run_evolution(self, callback=None):
        pop = self.toolbox.population(n=config.POPULATION_SIZE)
        fitness_history = []
        
        print(f"[Starting Evolution for Task: {self.task[:50]}]", flush=True)
        
        from concurrent.futures import ThreadPoolExecutor
        
        for gen in range(config.NUM_GENERATIONS):
            print(f"[Generation {gen+1}/{config.NUM_GENERATIONS} - Evaluating...]", flush=True)
            
            # Use ThreadPoolExecutor for parallel evaluation
            with ThreadPoolExecutor(max_workers=min(config.POPULATION_SIZE, 4)) as executor:
                fitnesses = list(executor.map(self.toolbox.evaluate, pop))
            
            for ind, fit in zip(pop, fitnesses):
                ind.fitness.values = fit
            
            best_ind = tools.selBest(pop, 1)[0]
            avg_fit = sum(ind.fitness.values[0] for ind in pop) / len(pop)
            fitness_history.append({"gen": gen + 1, "best": best_ind.fitness.values[0], "avg": avg_fit})
            
            print(f"[Generation {gen+1} Complete. Best Score: {best_ind.fitness.values[0]:.2f}]", flush=True)

            if callback:
                callback(gen, best_ind[0], best_ind.fitness.values[0])
            
            offspring = self.toolbox.select(pop, len(pop))
            offspring = list(map(self.toolbox.clone, offspring))

            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < 0.2:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values

            # Parallel mutation could also be done if needed, but mutation is usually fast
            for mutant in offspring:
                if random.random() < config.MUTATION_RATE:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values

            pop[:] = offspring

        return tools.selBest(pop, 1)[0][0], fitness_history