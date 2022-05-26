from typing import Optional

from scipy.interpolate import interpolate
from scipy.stats import uniform
import numpy as np
from config import get_mpe_config
from rae_types.agent import Agent
from rae_types.agent_type import AgentType

CONSPIRACY_THRESHOLD = 1
MULTIPLICATIVE_S_TYPE = "m"


class Service:
    def __init__(self, agent: Agent, supplier: Agent):
        self.receiver: Agent = agent
        self.provider: Agent = supplier
        self.provided_services: Optional[float] = None
        self.reported_services: Optional[float] = None

    def define_provided_services(self):
        available_services = self._generate_random_variable_using_inverse_transform(
            get_mpe_config().expoA
        )
        provider_threshold = self.define_threshold_value_for_provider()
        provided_services = self.define_provider_politics(
            available_services, provider_threshold
        )

        return provided_services

    def define_reported_services(self, provided_services:float):
        receiver_efficiency = self._generate_random_variable_using_inverse_transform(
            get_mpe_config().expoG
        )
        receiver_threshold = self.define_threshold_value_for_receiver()
        received_services = self.define_receiver_politics(
            provided_services, receiver_efficiency, receiver_threshold
        )
        return received_services

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
        # step function defined for (v, 1-x)
        return float(np.heaviside(good_will, (1 - partner_trust)))

    def define_threshold_value_for_receiver(self) -> float:
        mpe_config = get_mpe_config()
        if self.receiver.agent_type == AgentType.strategic.name:
            if mpe_config.scenario == 0:
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
            if mpe_config.scenario == 0:
                return mpe_config.good_will_y
            else:
                return 1.0
        else:
            return self.define_threshold_for_honest_agent(
                mpe_config.good_will_x, self.receiver.trust
            )
    def _generate_random_variable_using_inverse_transform(self, expo: float) -> float:
        U = uniform.rvs(size=1)
        X = -expo * np.log(1 - U)
        return X



