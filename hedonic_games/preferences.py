from hedonic_games import misc
from hedonic_games.stability import *


class Profile:

    def __init__(self, num_agents, agent_names=None):
        if num_agents <= 0:
            raise ValueError(f"{num_agents} is not a valid number of agents.")

        if agent_names:
            if len(agent_names) != num_agents:
                raise ValueError(
                    f"Number of agents {agent_names} does not match number of agent names {len(agent_names)}.")
            self.agent_names = list(map(str, agent_names))
        else:
            self.agent_names = list(map(str, range(num_agents)))

        self.agents = list(map(Agent, self.agent_names))
        for agent in self.agents:
            for other in self.agents:
                agent._add_other_agent(other)

    def __len__(self):
        return len(self.agents)

    def __str__(self):
        out = f"Profile with {len(self.agents)} agents: {str(self.agents)}\n"
        for agent in self.agents:
            out += f"{agent}: {agent.utilities}\n"
        return out

    def all_partitions(self):
        return [Partition(self, partition) for partition in misc.all_partitions(self.agents)]

    def has_stable_partition(self, stability_notion):
        return any(partition.is_stable(stability_notion) for partition in self.all_partitions())


class Agent:

    def __init__(self, agent_name):
        self.agent_name = agent_name
        self.agent_list = set()
        self.utilities = {}

    def __str__(self):
        return self.agent_name

    def __repr__(self):
        return self.agent_name

    def _add_other_agent(self, other_agent):
        self.agent_list.add(other_agent)
        self.utilities[other_agent] = 0

    def utility(self, coalition_or_agent):
        if type(coalition_or_agent) is Agent:
            other = coalition_or_agent
            return self.utilities[other]

        coalition = coalition_or_agent
        return sum(self.utilities[other] for other in coalition)


class Partition:

    def __init__(self, profile, coalitions):
        self.profile = profile
        self.coalitions = coalitions

    def __str__(self):
        return str(self.coalitions)

    def __repr__(self):
        return str(self.coalitions)

    def coalition_of(self, agent):
        for coalition in self.coalitions:
            if agent in coalition:
                return coalition

    def get_all_deviations(self, stability_notion=None):
        deviation = None

        for agent in self.profile.agents:
            left_coalition = self.coalition_of(agent)
            coalitions_to_consider = self.coalitions
            if len(left_coalition) != 1:
                coalitions_to_consider.append(set())
            for joined_coalition in coalitions_to_consider:
                if joined_coalition == left_coalition:
                    continue

                if deviation is None:
                    deviation = Deviation(self, agent, left_coalition, joined_coalition)
                else:
                    # Reuse previous Deviation object for efficiency
                    deviation.reset(self, agent, left_coalition, joined_coalition)

                if stability_notion is None or deviation.is_deviation_type(stability_notion):
                    yield deviation
                    deviation = None

    def is_stable(self, stability_notion):
        return next(self.get_all_deviations(stability_notion), None) is None

    def perform_deviation(self, deviation):
        if deviation.left_coalition not in self.coalitions or deviation.joined_coalition not in self.coalitions:
            raise ValueError("Deviation does not match partition.")

        deviation.left_coalition.remove(deviation.agent)
        deviation.joined_coalition.add(deviation.agent)


if __name__ == "__main__":
    profile = Profile(5)
    print(profile.all_partitions())
