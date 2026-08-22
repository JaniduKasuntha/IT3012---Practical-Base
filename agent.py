# agent.py
import random
from collections import deque
import heapq
import math

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
        different_unvisited = [move for move in unvisited_moves if move != self.last_action]

        if different_unvisited:
            action = random.choice(different_unvisited)
        elif unvisited_moves:
            # Prefer moving into unexplored territory
            action = random.choice(unvisited_moves)
        else:
            # Fallback: If all surrounding directions are visited, pick any valid move to escape
            action = random.choice(list(candidates.keys()))

        self.last_action = action
        return action

class SearchAgent:
    """A problem-solving agent that uses search algorithms to find paths in a grid."""

    def __init__(self, active_algo='AStar'):
        self.plan = []
        self.active_algo = active_algo
        self.x = 0
        self.y = 0
        self.last_action = None

    def sense_and_act(self, percept: dict) -> str:
        if "agent_pos" in percept:
            current_pos = tuple(percept["agent_pos"])
            self.x, self.y = current_pos
        else:
            if self.last_action == 'Up':
                self.y += 1
            elif self.last_action == 'Down':
                self.y -= 1
            elif self.last_action == 'Left':
                self.x -= 1
            elif self.last_action == 'Right':
                self.x += 1
            current_pos = (self.x, self.y)

        if not self.plan:
            food_list = percept.get('all_food') or percept.get('food_positions') or []
            if not food_list:
                return 'Stay'

            # Find closest food pellet using Manhattan distance
            closest_food = min(
                food_list,
                key=lambda f: abs(f[0] - current_pos[0]) + abs(f[1] - current_pos[1])
            )

            grid_size = percept.get('grid_size', (10, 10))
            walls = percept.get('walls', [])

            if self.active_algo == 'BFS':
                actions = self.bfs_search(current_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'DFS':
                actions = self.dfs_search(current_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'UCS':
                actions = self.ucs_search(current_pos, closest_food, walls, grid_size)
            elif self.active_algo == 'AStar' or self.active_algo == 'A*':
                actions = self.astar_search(current_pos, closest_food, walls, grid_size)
            else:
                actions = self.bfs_search(current_pos, closest_food, walls, grid_size)

            if actions:
                self.plan = list(actions)

        if self.plan:
            action = self.plan.pop(0)
            self.last_action = action
            return action

        return 'Stay'



    def _get_neighbors(self, state, walls, grid_size):
        x, y = state
        width, height = grid_size
        wall_set = set(walls) if not isinstance(walls, set) else walls

        moves = [
            ('Up', (x, y + 1)),
            ('Down', (x, y - 1)),
            ('Left', (x - 1, y)),
            ('Right', (x + 1, y))
        ]

        neighbors = []
        for action, (nx, ny) in moves:
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in wall_set:
                neighbors.append((action, (nx, ny)))
        return neighbors

    def bfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Breadth-First Search (BFS) using a FIFO queue (deque.popleft()).

        Explores the shallowest nodes first.
        """
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if start == goal:
            return []

        queue = deque([(start, [])])
        visited = {start}

        while queue:
            current, path = queue.popleft()

            if current == goal:
                return path

            for action, neighbor in self._get_neighbors(current, walls, grid_size):
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [action]
                    if neighbor == goal:
                        return new_path
                    queue.append((neighbor, new_path))

        return None

    def dfs_search(self, start_pos, goal_pos, walls, grid_size):
        """Depth-First Search (DFS) using a LIFO stack (list.pop()).

        Explores the deepest nodes first.
        """
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if start == goal:
            return []

        stack = [(start, [])]
        visited = set()

        while stack:
            current, path = stack.pop()

            if current == goal:
                return path

            if current not in visited:
                visited.add(current)
                for action, neighbor in self._get_neighbors(current, walls, grid_size):
                    if neighbor not in visited:
                        stack.append((neighbor, path + [action]))

        return None

    def ucs_search(self, start_pos, goal_pos, walls, grid_size, cost_fn=None):
        """Uniform-Cost Search (UCS) using a Priority Queue (heapq.heappop()).

        Ordered by total path cost g(n).
        """
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if start == goal:
            return []

        counter = 0
        pq = [(0, counter, start, [])]
        visited = set()

        while pq:
            cost, _, current, path = heapq.heappop(pq)

            if current == goal:
                return path

            if current in visited:
                continue

            visited.add(current)

            for action, neighbor in self._get_neighbors(current, walls, grid_size):
                if neighbor not in visited:
                    step_cost = 1
                    if callable(cost_fn):
                        step_cost = cost_fn(current, action, neighbor)
                    elif isinstance(cost_fn, dict):
                        step_cost = cost_fn.get((current, action), 1)
                    elif isinstance(cost_fn, (int, float)):
                        step_cost = cost_fn

                    counter += 1
                    heapq.heappush(pq, (cost + step_cost, counter, neighbor, path + [action]))

        return None

    def manhattan_distance(self, pos, goal):
        """Calculates Manhattan distance h(n) = |x1 - x2| + |y1 - y2|."""
        return int(abs(pos[0] - goal[0]) + abs(pos[1] - goal[1]))

    def euclidean_distance(self, pos, goal):
        """Calculates Euclidean distance h(n) = sqrt((x1 - x2)^2 + (y1 - y2)^2)."""
        return math.sqrt((pos[0] - goal[0])**2 + (pos[1] - goal[1])**2)

    def astar_search(self, start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan'):
        """A* Search algorithm using a Priority Queue (heapq).

        Tuple format: (f_cost, g_cost, current_pos, path_taken)
        """
        start = tuple(start_pos)
        goal = tuple(goal_pos)

        if start == goal:
            return []

        def calc_h(pos):
            if heuristic_type == 'euclidean':
                return self.euclidean_distance(pos, goal)
            return self.manhattan_distance(pos, goal)

        pq = []
        reached_states = set()

        g_start = 0
        h_start = calc_h(start)
        f_start = g_start + h_start

        heapq.heappush(pq, (f_start, g_start, start, []))

        while pq:
            f_cost, g_cost, current_pos, path_taken = heapq.heappop(pq)

            if current_pos == goal:
                return path_taken

            if current_pos in reached_states:
                continue

            reached_states.add(current_pos)

            for action, neighbor in self._get_neighbors(current_pos, walls, grid_size):
                if neighbor not in reached_states:
                    g_new = g_cost + 1
                    h_new = calc_h(neighbor)
                    f_new = g_new + h_new
                    heapq.heappush(pq, (f_new, g_new, neighbor, path_taken + [action]))

        return None


if __name__ == '__main__':
    agent = SearchAgent()
    start_pos = (0, 0)
    goal_pos = (3, 4)

    manhattan_res = agent.manhattan_distance(start_pos, goal_pos)
    euclidean_res = agent.euclidean_distance(start_pos, goal_pos)

    print("=== Testing Checkpoint ===")
    print(f"Start: {start_pos}, Goal: {goal_pos}")
    print(f"Manhattan Distance: {manhattan_res}")
    print(f"Euclidean Distance: {euclidean_res}")

    grid_size = (4, 4)
    walls = [(1, 0), (2, 0), (0, 2), (1, 2), (2, 2)]
    start = (0, 0)
    goal = (3, 3)
    path_m = agent.astar_search(start, goal, walls, grid_size, heuristic_type='manhattan')
    path_e = agent.astar_search(start, goal, walls, grid_size, heuristic_type='euclidean')
    print("\n=== A* Search Checkpoint ===")
    print(f"A* (Manhattan) Path: {path_m}")
    print(f"A* (Euclidean) Path: {path_e}")

