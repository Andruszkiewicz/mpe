from enum import Enum
from typing import List

from rae_types.agent import Agent
from rae_types.service import Service


class AgentServices(Enum):
    agent: Agent
    services: List[Service]
