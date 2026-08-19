# agent.py
import random
from collections import deque 
import heapq

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
            return "Down"
class ModelBasedAgent:
    """A Model-Based agent with internal state and memory to avoid visiting duplicate cells and break loops."""

    def __init__(self):
        self.x = 0
        self.y = 0
        self.visited_cells = {(0, 0)}
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        # Step 1: Transition Model - Update internal coordinates based on last action taken
        if self.last_action == 'Up':
            self.y += 1
        elif self.last_action == 'Down':
            self.y -= 1
        elif self.last_action == 'Left':
            self.x -= 1
        elif self.last_action == 'Right':
            self.x += 1

        # Sensor Model - Record current state in memory
        self.visited_cells.add((self.x, self.y))

        # Rule 1: Eat food if present
        if percept.get("food_here"):
            action = "Stay"
            self.last_action = action
            return action

        # Map possible candidate moves to target relative coordinates
        candidates = {
            'Up': (self.x, self.y + 1),
            'Down': (self.x, self.y - 1),
            'Left': (self.x - 1, self.y),
            'Right': (self.x + 1, self.y)
        }

        # Sensor Check: Eliminate 'Up' if a wall is directly ahead
        if percept.get("wall_ahead") and 'Up' in candidates:
            del candidates['Up']

        # Step 2: Query Memory - Filter out already visited coordinates
        unvisited_moves = [move for move, pos in candidates.items() if pos not in self.visited_cells]

        if unvisited_moves:
            # Prefer moving into unexplored territory
            action = random.choice(unvisited_moves)
        else:
            # Fallback: If all surrounding directions are visited, pick any valid move to escape
            action = random.choice(list(candidates.keys()))

        self.last_action = action
        return action
