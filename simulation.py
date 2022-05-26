import copy
import random
from typing import List

from config import MPEConfig
from rae_types.agent import Agent
from rae_types.agent_type import AgentType
import numpy as np

from rae_types.service import Service


def run_simulation(mpe_config: MPEConfig):
    agents: List[Agent] = create_agents(mpe_config)

    for cycle in range(mpe_config.cycle_count):
        agents_with_assigned_suppliers: List[Agent] = assign_suppliers(
            agents, mpe_config
        )
        services: List[Service] = perform_services(agents_with_assigned_suppliers)
        print(services)
        print([(service.provided_services, service.reported_services) for service in services])
        # rae(service)


def perform_services(agents: List[Agent]) -> List[Service]:
    services = []
    for agent in agents:
        for supplier in agent.suppliers:
            service: Service = Service(agent, supplier)
            service.provided_services = service.define_provided_services()
            service.reported_services = service.define_reported_services(
                service.provided_services
            )
            services.append(service)
    return services


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


def assign_suppliers(agents: List[Agent], mpe_config: MPEConfig) -> List[Agent]:
    agents_with_assigned_suppliers: List[Agent] = []
    recipients = copy.deepcopy(agents)

    for agent in recipients:
        suppliers_count = np.random.randint(mpe_config.k_min, mpe_config.k_max)
        agent.suppliers = draw_suppliers(
            recipient=agent, agents=agents, count=suppliers_count
        )
        agents_with_assigned_suppliers.append(agent)

    return agents_with_assigned_suppliers


def draw_suppliers(recipient: Agent, agents: List[Agent], count: int) -> List[Agent]:
    return random.sample([agent for agent in agents if agent.id != recipient.id], count)
