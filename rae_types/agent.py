from typing import Optional, List



class Agent:
    def __init__(
        self,
        id: int,
        trust: float,
        agent_type: str,
        reputation: Optional[float] = None,
        providers: List["Agent"] = None,
    ):
        self.id = id
        self.trust = trust
        self.agent_type = agent_type
        self.reputation = reputation
        self.providers = providers

