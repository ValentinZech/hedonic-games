from hedonic_games.preferences import Profile
from random import randint, random


def random_profile(num_agents, min_util=-100, max_util=100, symmetry_prop=0.0):
    profile = Profile(num_agents)

    for i, a1 in enumerate(profile.agents):
        for a2 in profile.agents[i+1:]:
            val = randint(min_util, max_util)
            a1.utilities[a2] = val
            if random() > symmetry_prop:
                val = randint(min_util, max_util)
            a2.utilities[a1] = val

    return profile


if __name__ == '__main__':
    profile = random_profile(5, symmetry_prop=0.1)
    print(profile)
