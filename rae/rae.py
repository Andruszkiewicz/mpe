from statistics import mean
from typing import List, Dict, Optional, Tuple

import numpy
from sklearn.cluster import KMeans
from config import get_mpe_config
from rae_types.agent import Agent
from rae_types.agent_type import AgentType
from rae_types.service import Service


class ReputationAggregationEngine:
    def __init__(self):
        self.cycles_history: Dict[int, Dict[Agent, List[Service]]] = {}
        self.trust_history_per_agent_type: Dict[int, Dict[str, float]] = {}

    def calculate_trust(
        self, agent_services: Dict[Agent, List[Service]], all_agents: List[Agent]
    ) -> List[Agent]:
        mean_reported_services_per_provider: Dict[Agent, float] = self.report_services(
            agent_services, all_agents
        )
        cluster_a, cluster_b = self.perform_clustering(
            mean_reported_services_per_provider
        )
        all_agents = self.assign_trust(
            all_agents, cluster_a, cluster_b, mean_reported_services_per_provider
        )
        self.update_trust_history_per_agent_type(all_agents)

        return all_agents

    def report_services(
        self, agent_services: Dict[Agent, List[Service]], all_agents: List[Agent]
    ) -> Dict[Agent, float]:

        current_cycle: int = len(self.cycles_history.keys()) + 1
        self.cycles_history[current_cycle] = agent_services

        mean_reported_services_per_provider: Dict[Agent, float] = {}

        for provider, services in agent_services.items():
            mean_reported_services: List[float] = []
            for agent in all_agents:
                (
                    last_interaction_cycle,
                    last_reported_services,
                ) = self.get_last_interaction_cycle(provider, agent)
                if last_interaction_cycle:
                    delta_interaction = current_cycle - last_interaction_cycle
                    if delta_interaction < current_cycle:
                        mean_reported_services.append(
                            agent.trust
                            * (get_mpe_config().delta ** delta_interaction)
                            * last_reported_services
                        )
                    else:
                        RuntimeError()

            mean_reported_services_per_provider[provider] = mean(mean_reported_services)

        return mean_reported_services_per_provider

    def get_last_interaction_cycle(
        self, provider: Agent, receiver: Agent
    ) -> Tuple[Optional[int], Optional[float]]:

        last_cycle = None
        last_reported_services = None

        for cycle, agent_services in reversed(self.cycles_history.items()):
            cycle_services_for_provider = agent_services.get(provider)
            if cycle_services_for_provider:
                for service in cycle_services_for_provider:
                    if service.receiver == receiver:
                        last_cycle = cycle
                        last_reported_services = service.reported_services
                        break

        return last_cycle, last_reported_services

    def perform_clustering(
        self, mean_reported_services_per_provider: Dict[Agent, float]
    ) -> Tuple[List[Agent], List[Agent]]:
        kmeans = KMeans(2)

        b = numpy.array(list(mean_reported_services_per_provider.values())).reshape(
            -1, 1
        )

        providers_clusters = kmeans.fit_predict(b)

        cluster_a = []
        cluster_b = []

        for provider_cluster, provider in zip(
            providers_clusters, mean_reported_services_per_provider.keys()
        ):
            if provider_cluster == 0:
                cluster_a.append(provider)
            else:
                cluster_b.append(provider)

        return (cluster_a, cluster_b)

    def assign_trust(
        self,
        all_agents: List[Agent],
        cluster_high,
        cluster_low,
        mean_reported_services_per_provider,
    ):
        mean_reported_services_in_cluster_a = mean(
            [mean_reported_services_per_provider[provider] for provider in cluster_high]
        )
        mean_reported_services_in_cluster_b = mean(
            [mean_reported_services_per_provider[provider] for provider in cluster_low]
        )

        if mean_reported_services_in_cluster_a > mean_reported_services_in_cluster_b:
            trust_low = (
                mean_reported_services_in_cluster_b
                / mean_reported_services_in_cluster_a
            )
            trust_high = 1
        else:
            trust_low = (
                mean_reported_services_in_cluster_a
                / mean_reported_services_in_cluster_b
            )
            trust_high = 1

        for agent in all_agents:
            if agent in cluster_high:
                agent.trust = trust_high
            elif agent in cluster_low:
                agent.trust = trust_low

        return all_agents

    def update_trust_history_per_agent_type(self, all_agents: List[Agent]):
        trust_of_honest_agents_list = []
        trust_of_strategic_agents_list = []

        current_cycle = len(self.trust_history_per_agent_type) + 1

        for agent in all_agents:
            if agent.agent_type == AgentType.strategic.name:
                trust_of_strategic_agents_list.append(agent.trust)
            elif agent.agent_type == AgentType.honest.name:
                trust_of_honest_agents_list.append(agent.trust)

        self.trust_history_per_agent_type[current_cycle] = {
            AgentType.strategic.name: mean(trust_of_strategic_agents_list),
            AgentType.honest.name: mean(trust_of_honest_agents_list),
        }
