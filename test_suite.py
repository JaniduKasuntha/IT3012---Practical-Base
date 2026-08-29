import unittest
from agent import SimpleReflexAgent, ModelBasedAgent, SearchAgent


class TestPractical1And2_ReflexAgents(unittest.TestCase):
    """
    Tests for Practicals 1 & 2: Simple Reflex and Model-Based Agents.
    Focuses on Condition-Action rules, partial observability, and memory.
    """

    def setUp(self):
        # Instantiate agents (assuming students have created these classes)
        try:
            self.simple_agent = SimpleReflexAgent()
            self.model_agent = ModelBasedAgent()
        except NameError:
            self.fail("Agent classes not found. Ensure SimpleReflexAgent and ModelBasedAgent are defined.")

    def test_simple_reflex_logic(self):
        """Test 1: Simple Reflex Agent should react purely to immediate percepts."""
        # Scenario A: Food is present -> Agent should want to collect/stay/move appropriately
        percept_food = {'wall_ahead': False, 'food_here': True}
        action = self.simple_agent.sense_and_act(percept_food)
        self.assertIsNotNone(action, "SimpleReflexAgent returned None instead of an action.")

        # Scenario B: Wall is ahead -> Agent must turn or change direction
        percept_wall = {'wall_ahead': True, 'food_here': False}
        action_wall = self.simple_agent.sense_and_act(percept_wall)
        self.assertIn(action_wall, ['Left', 'Right', 'Down', 'Up'],
                      "Agent did not output a valid movement action when facing a wall.")

    def test_model_based_memory(self):
        """Test 2: Model-Based Agent should maintain internal state to escape loops."""
        # Feed the exact same percept twice to simulate being stuck in a corner
        percept = {'wall_ahead': True, 'food_here': False}

        action_1 = self.model_agent.sense_and_act(percept)
        action_2 = self.model_agent.sense_and_act(percept)

        # A simple reflex agent would return the exact same action twice.
        # A model-based agent should remember the previous failure and try a DIFFERENT action.
        self.assertNotEqual(
            action_1,
            action_2,
            "ModelBasedAgent returned the exact same action twice in a row for the same percept. Internal state/memory is not working correctly."
        )


class TestPractical3_SearchAgent(unittest.TestCase):
    """
    Tests for Practical 3: Problem-Solving Agents.
    Focuses on offline planning and Breadth-First Search (BFS) implementation.
    """

    def setUp(self):
        try:
            self.search_agent = SearchAgent()
        except NameError:
            self.fail("SearchAgent class not found.")

    def test_bfs_shortest_path(self):
        """Test 3: BFS must find the optimal (shortest) path in a static maze."""
        # Mock Environment Data
        grid_size = (4, 4)
        start_pos = (0, 0)
        goal_pos = (3, 3)

        # Create a U-shaped wall trap that the agent must navigate around
        # Grid layout (S=Start, G=Goal, W=Wall):
        # 3 | . . . G
        # 2 | W W W .
        # 1 | . . . .
        # 0 | S W W .
        #   ---------
        #     0 1 2 3
        walls = [(1, 0), (2, 0), (0, 2), (1, 2), (2, 2)]

        # Run student's BFS algorithm
        try:
            path = self.search_agent.bfs_search(start_pos, goal_pos, walls, grid_size)
        except AttributeError:
            self.fail("bfs_search method not implemented in SearchAgent.")

        # Verify the path is valid and optimal
        self.assertIsNotNone(path, "BFS returned None. No path found.")
        self.assertIsInstance(path, list, "BFS should return a list of actions (strings).")

        # The shortest path taking Manhattan distance around these specific walls is exactly 6 steps.
        # Path: Up -> Right -> Right -> Right -> Up -> Up
        self.assertEqual(len(path), 6, f"BFS did not find the optimal path. Expected 6 steps, got {len(path)}.")

    def test_bfs_unreachable_goal(self):
        """Test 4: BFS must correctly return failure (None/Empty) if goal is blocked."""
        grid_size = (3, 3)
        start_pos = (0, 0)
        goal_pos = (2, 2)

        # Box the goal in completely
        walls = [(1, 2), (2, 1), (1, 1)]

        path = self.search_agent.bfs_search(start_pos, goal_pos, walls, grid_size)

        # The agent should realize it's impossible and return None or an empty list
        is_empty_or_none = (path is None) or (len(path) == 0)
        self.assertTrue(is_empty_or_none, "BFS should return None or [] when the goal is unreachable.")

    def test_heuristic_distances(self):
        """Test 5: Manhattan and Euclidean distance heuristics."""
        pos = (1, 2)
        goal = (4, 6)
        # Manhattan: |1-4| + |2-6| = 3 + 4 = 7
        m_dist = self.search_agent.manhattan_distance(pos, goal)
        self.assertEqual(m_dist, 7, f"Expected Manhattan distance 7, got {m_dist}")
        self.assertIsInstance(m_dist, int, "Manhattan distance must return an integer.")

        # Euclidean: sqrt((1-4)^2 + (2-6)^2) = sqrt(9 + 16) = 5.0
        e_dist = self.search_agent.euclidean_distance(pos, goal)
        self.assertAlmostEqual(e_dist, 5.0, places=5, msg=f"Expected Euclidean distance 5.0, got {e_dist}")

    def test_astar_search(self):
        """Test 6: A* Search finds the optimal path with both heuristics."""
        grid_size = (4, 4)
        start_pos = (0, 0)
        goal_pos = (3, 3)
        walls = [(1, 0), (2, 0), (0, 2), (1, 2), (2, 2)]

        # Test Manhattan heuristic
        path_m = self.search_agent.astar_search(start_pos, goal_pos, walls, grid_size, heuristic_type='manhattan')
        self.assertIsNotNone(path_m, "A* (Manhattan) returned None.")
        self.assertEqual(len(path_m), 6, f"Expected 6 steps for optimal path, got {len(path_m)}")

        # Test Euclidean heuristic
        path_e = self.search_agent.astar_search(start_pos, goal_pos, walls, grid_size, heuristic_type='euclidean')
        self.assertIsNotNone(path_e, "A* (Euclidean) returned None.")
        self.assertEqual(len(path_e), 6, f"Expected 6 steps for optimal path, got {len(path_e)}")


class TestKnowledgeBase(unittest.TestCase):
    """
    Tests for Step 1.1: Knowledge Base and Forward Chaining logic engine.
    """

    def test_knowledge_base_forward_chaining(self):
        from logic_engine import KnowledgeBase
        kb = KnowledgeBase()
        
        kb.tell_rule(["HasVision", "EnemySpotted"], "ThreatDetected")
        kb.tell_rule(["ThreatDetected", "LowHealth"], "RetreatNeeded")
        
        kb.tell_fact("HasVision")
        kb.tell_fact("EnemySpotted")
        kb.tell_fact("LowHealth")
        
        kb.forward_chain()
        
        self.assertTrue(kb.ask("ThreatDetected"), "Forward chaining failed to infer 'ThreatDetected'.")
        self.assertTrue(kb.ask("RetreatNeeded"), "Forward chaining failed to infer 'RetreatNeeded'.")
        self.assertFalse(kb.ask("UnknownFact"), "KnowledgeBase incorrectly contains un-entailed fact.")

    def test_clear_facts(self):
        from logic_engine import KnowledgeBase
        kb = KnowledgeBase()
        kb.tell_fact("Fact1")
        kb.clear_facts()
        self.assertEqual(len(kb.facts), 0, "clear_facts() did not empty the facts set.")

    def test_agent_kb_rules(self):
        from agent import SearchAgent
        agent = SearchAgent()
        
        # Test Rule 1: TargetVisible ∧ HasDust ⇒ SafeToEngage
        agent.kb.tell_fact("TargetVisible")
        agent.kb.tell_fact("HasDust")
        agent.kb.forward_chain()
        self.assertTrue(agent.kb.ask("SafeToEngage"), "SafeToEngage rule failed.")

        # Test Rule 2: SafeToEngage ∧ BloodseekerMissing ⇒ Retreat
        agent.kb.tell_fact("BloodseekerMissing")
        agent.kb.forward_chain()
        self.assertTrue(agent.kb.ask("Retreat"), "Retreat rule failed.")

    def test_astar_kb_feasibility(self):
        from agent import SearchAgent
        agent = SearchAgent()
        
        grid_size = (3, 3)
        start = (0, 0)
        goal = (2, 0)
        walls = []

        # Tile (1, 0) is physically open, but logically infeasible due to Retreat percepts
        tile_percepts = {
            (1, 0): ['TargetVisible', 'HasDust', 'BloodseekerMissing']
        }

        path = agent.astar_search(start, goal, walls, grid_size, tile_percepts=tile_percepts)
        # Agent should avoid (1, 0) and route around via (0, 1) -> (1, 1) -> (2, 1) -> (2, 0)
        self.assertIsNotNone(path, "A* failed to find path around infeasible tile.")
        
        # Compute visited positions along the path
        curr = list(start)
        visited_coords = []
        for move in path:
            if move == 'Up': curr[1] += 1
            elif move == 'Down': curr[1] -= 1
            elif move == 'Left': curr[0] -= 1
            elif move == 'Right': curr[0] += 1
            visited_coords.append(tuple(curr))

        self.assertNotIn((1, 0), visited_coords, "Tile (1,0) should be avoided by A* path.")
        self.assertEqual(len(path), 4, f"Expected detour path of length 4, got {len(path)}: {path}")





if __name__ == '__main__':
    # Run the test suite
    print("=== IT3012: Intelligent Agents - Autograder Test Suite ===\n")
    unittest.main(verbosity=2)
