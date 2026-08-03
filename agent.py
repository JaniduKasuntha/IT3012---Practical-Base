# agent.py
import random

class GreedyGridAgent:
    """A simple agent that tries to move around systematically to clear the grid."""

    def __init__(self):
        self.actions_pool = ['Up', 'Down', 'Left', 'Right']

    def sense_and_act(self, percept: dict) -> str:
        # Simple heuristic or fallback random sweep
        return random.choice(self.actions_pool)

    class SimpleReflexAgent:
        def sense_and_act(self, percept):

            # Rule 1
            if percept["food_here"]:
                return "Stay"

            # Rule 2
            elif percept["wall_ahead"]:
                return random.choice(["Left", "Right"])

            # Rule 3
            else:
                return "Up"