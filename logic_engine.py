class KnowledgeBase:
    """
    A declarative Knowledge Base storing Facts (set of strings) 
    and Rules (Horn clauses represented as (premise_list, conclusion_string)).
    Supports Forward Chaining inference using Modus Ponens.
    """

    def __init__(self):
        self.facts = set()  # To store unique string facts (e.g., "TargetVisible")
        self.rules = []     # To store rules as tuples: ([list_of_premises], "conclusion_string")

    def tell_fact(self, fact_string: str):
        """Add a fact string to the Knowledge Base."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list: list, conclusion_string: str):
        """Add a Horn Clause rule (premises => conclusion) to the Knowledge Base."""
        self.rules.append((list(premise_list), conclusion_string))

    def clear_facts(self):
        """Empty all facts from the Knowledge Base (useful for re-evaluating percepts per step)."""
        self.facts.clear()

    def ask(self, query_string: str) -> bool:
        """Check if a specific fact is currently known/inferred in the Knowledge Base."""
        return query_string in self.facts

    def forward_chain(self):
        """
        Executes Forward Chaining inference engine over Horn Clauses using Modus Ponens.
        Repeatedly evaluates rules against current facts to derive new facts until no more facts can be derived.
        """
        new_facts_added = True

        while new_facts_added:
            new_facts_added = False

            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    # Modus Ponens Check: If ALL premises are in facts
                    if all(p in self.facts for p in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True


if __name__ == "__main__":
    print("=== Testing KnowledgeBase & Forward Chaining ===")
    kb = KnowledgeBase()

    # Define Horn Clause Rules
    kb.tell_rule(["HasVision", "EnemySpotted"], "ThreatDetected")
    kb.tell_rule(["ThreatDetected", "LowHealth"], "RetreatNeeded")
    kb.tell_rule(["RetreatNeeded"], "InfeasibleStep")

    # Add Percept Facts
    kb.tell_fact("HasVision")
    kb.tell_fact("EnemySpotted")
    kb.tell_fact("LowHealth")

    print("Initial Facts:", kb.facts)
    kb.forward_chain()
    print("Inferred Facts:", kb.facts)
    print("Is RetreatNeeded entailed?", kb.ask("RetreatNeeded"))
    print("Is InfeasibleStep entailed?", kb.ask("InfeasibleStep"))