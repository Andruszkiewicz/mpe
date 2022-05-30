import random
from collections import defaultdict
from typing import List, Dict, DefaultDict
from scipy.stats import uniform
from config import MPEConfig, get_mpe_config
from rae.rae import ReputationAggregationEngine
from rae_types.agent import Agent
from rae_types.agent_type import AgentType
import numpy as np
from rae_types.service import Service
import matplotlib.pyplot as plt
import csv


def run_simulation(mpe_config: MPEConfig):
    agents: List[Agent] = create_agents(mpe_config)
    rae: ReputationAggregationEngine = ReputationAggregationEngine()

    for cycle in range(mpe_config.cycle_count):
        print(cycle)
        random_inverse_transform_distribution_A = generate_random_inverse_distribuant_distribution(
            mpe_config.expoA
        )
        random_inverse_transform_distribution_G = generate_random_inverse_distribuant_distribution(
            mpe_config.expoG
        )
        agents_with_assigned_providers: List[Agent] = assign_providers(
            agents, mpe_config
        )
        agent_services: Dict[Agent, List[Service]] = perform_services(
            agents_with_assigned_providers,
            random_inverse_transform_distribution_A,
            random_inverse_transform_distribution_G,
        )
        agents = rae.calculate_trust(agent_services, agents_with_assigned_providers)

    plot_trust_per_agent_type(rae.trust_history_per_agent_type)
    save_results_to_csv(rae.trust_history_per_agent_type)


def save_results_to_csv(trust_history_per_agent_type: Dict[int, Dict[str, float]]):
    f = open("results.csv", "w")
    writer = csv.writer(f)
    mpe_config = get_mpe_config()
    writer.writerow(("Config key", "Value"))
    for key, value in mpe_config.__dict__.items():
        writer.writerow((key, value))

    writer.writerow([])
    writer.writerow(("Cycle", "Trust Honest avg", "Trust Strategic avg"))

    for cycle_count, trust_per_agent_type in trust_history_per_agent_type.items():
        writer.writerow(
            (
                cycle_count,
                trust_per_agent_type[AgentType.honest.name],
                trust_per_agent_type[AgentType.strategic.name],
            )
        )
    f.close()


def plot_trust_per_agent_type(
    trust_history_per_agent_type: Dict[int, Dict[str, float]]
):
    honest_agents_trust_through_cycles = []
    strategic_agents_trust_through_cycles = []

    for cycle_count, trust_per_agent_type in trust_history_per_agent_type.items():
        honest_agents_trust_through_cycles.append(
            trust_per_agent_type[AgentType.honest.name]
        )
        strategic_agents_trust_through_cycles.append(
            trust_per_agent_type[AgentType.strategic.name]
        )

    plt.plot(
        trust_history_per_agent_type.keys(),
        honest_agents_trust_through_cycles,
        label="Honest",
    )
    plt.plot(
        trust_history_per_agent_type.keys(),
        strategic_agents_trust_through_cycles,
        label="Strategic",
    )
    plt.ylabel("Trust")
    plt.legend()
    plt.show()


def generate_random_inverse_distribuant_distribution(expo: int) -> List[float]:
    U = uniform.rvs(size=100000)
    random_inverse_distribuant_distribution = []
    for u in U:
        random_inverse_distribuant_distribution.append(u ** (1 / expo))
    return random_inverse_distribuant_distribution


def perform_services(
    agents: List[Agent],
    random_inverse_transform_distribution_A: List[float],
    random_inverse_transform_distribution_G: List[float],
) -> Dict[Agent, List[Service]]:

    agent_services: DefaultDict = defaultdict(list)

    for agent in agents:
        for provider in agent.providers:
            service: Service = Service(
                agent,
                provider,
                random_inverse_transform_distribution_A,
                random_inverse_transform_distribution_G,
            )
            service.provided_services = service.define_provided_services()
            service.reported_services = service.define_reported_services(
                service.provided_services
            )
            agent_services[provider].append(service)

    return agent_services


def create_agents(mpe_config: MPEConfig) -> List[Agent]:
    s_agents: List[Agent] = [
        Agent(id=i, trust=mpe_config.V_0, agent_type=AgentType.strategic.name)
        for i in range(mpe_config.s_agent_count)
    ]
    h_agents: List[Agent] = [
        Agent(
            id=len(s_agents) + i, trust=mpe_config.V_0, agent_type=AgentType.honest.name
        )
        for i in range(mpe_config.agent_count - mpe_config.s_agent_count)
    ]

    return s_agents + h_agents


def assign_providers(agents: List[Agent], mpe_config: MPEConfig) -> List[Agent]:
    agents_with_assigned_providers: List[Agent] = []

    for agent in agents:
        providers_count = np.random.randint(mpe_config.k_min, mpe_config.k_max)
        agent.providers = draw_providers(
            recipient=agent, agents=agents, count=providers_count
        )
        agents_with_assigned_providers.append(agent)

    return agents_with_assigned_providers


def draw_providers(recipient: Agent, agents: List[Agent], count: int) -> List[Agent]:
    return random.sample([agent for agent in agents if agent.id != recipient.id], count)
