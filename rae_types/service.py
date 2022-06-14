import random
from typing import Optional, List
import numpy as np
from config import get_mpe_config
from rae_types.agent import Agent
from rae_types.agent_type import AgentType

CONSPIRACY_THRESHOLD = 1
MULTIPLICATIVE_S_TYPE = "m"


class Service:
    def __init__(
        self,
        receiver: Agent,
        provider: Agent,
        available_services: float,
        receiver_efficiency: float,
    ):
        self.receiver: Agent = receiver
        self.provider: Agent = provider
        self.available_services = (
            available_services
        )
        self.receiver_efficiency = (
            receiver_efficiency
        )
        self.provided_services: Optional[float] = None
        self.reported_services: Optional[float] = None

    def define_provided_services(self):
        provider_threshold = self.define_threshold_value_for_provider() #provider honest receiver strategic
        provided_services = self.define_provider_politics(
            self.available_services, provider_threshold
        )

        return provided_services

    def define_reported_services(self, provided_services: float):
        receiver_threshold = self.define_threshold_value_for_receiver()
        reported_services = self.define_receiver_politics(
            provided_services, self.receiver_efficiency, receiver_threshold
        )
        return reported_services

    def define_provider_politics(
        self, available_services: float, provider_threshold: float
    ) -> float:
        if get_mpe_config().s_type.lower() == MULTIPLICATIVE_S_TYPE:
            return available_services * provider_threshold
        else:
            return min(available_services, provider_threshold)

    def define_receiver_politics(
        self,
        provider_politics: float,
        receiver_efficiency: float,
        receiver_threshold: float,
    ) -> float:
        if get_mpe_config().s_type.lower() == MULTIPLICATIVE_S_TYPE:
            return receiver_efficiency * provider_politics * receiver_threshold
        else:
            return min(receiver_efficiency * provider_politics, receiver_threshold)

    def define_threshold_for_honest_agent(
        self, good_will: float, partner_trust: float
    ) -> float:
        if (1 - good_will) >= partner_trust:
            return 1.0
        else:
            return 0.0

    def define_threshold_value_for_receiver(self) -> float:
        mpe_config = get_mpe_config()
        if self.receiver.agent_type == AgentType.strategic.name:
            if mpe_config.scenario == 0 or self.provider.agent_type == AgentType.honest:
                return mpe_config.good_will_z
            else:
                return 1.0
        else:
            return self.define_threshold_for_honest_agent(
                mpe_config.good_will_x, self.provider.trust
            )

    def define_threshold_value_for_provider(self) -> float:
        mpe_config = get_mpe_config()
        if self.provider.agent_type == AgentType.strategic.name:
            if mpe_config.scenario == 0 or self.receiver.agent_type == AgentType.honest:
                return mpe_config.good_will_y
            else:
                return 1.0
        else:
            return self.define_threshold_for_honest_agent(
                mpe_config.good_will_x, self.receiver.trust
            )

    def _generate_random_variable_from_distribution(
        self, distribution: List[float]
    ) -> float:
        # check out seed influence
        return random.choice(distribution)
