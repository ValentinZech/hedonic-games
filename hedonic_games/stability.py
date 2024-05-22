from hedonic_games import misc

from enum import Enum
from dataclasses import dataclass
from typing import Optional

try:
    from gmpy2 import mpq as Fraction
except ImportError as e:
    misc.print_strerr(e)
    from fractions import Fraction


class StabilityEnum(Enum):
    Nash = 0
    Individual = 1
    Contractual = 2
    ContractualIndividual = 3
    VoteIn = 4
    VoteOut = 5
    VoteJoined = 6
    VoteSeparate = 7


@dataclass
class StabilityNotion:
    notion: StabilityEnum
    vote_in_quota: Optional[Fraction] = Fraction(1, 2)
    vote_out_quota: Optional[Fraction] = Fraction(1, 2)
    vote_joined_quota: Optional[Fraction] = Fraction(1, 2)

    def __post_init__(self):
        if any(type(quota) is not Fraction for quota in
               (self.vote_in_quota, self.vote_out_quota, self.vote_joined_quota)):
            raise ValueError("Vote quotas must be Fractions")


class Deviation:

    def __init__(self, partition, agent, left_coalition, joined_coalition):
        self.partition = partition
        self.agent = agent
        self.left_coalition = left_coalition
        self.joined_coalition = joined_coalition
        self.is_nash = self.agent.utility(self.joined_coalition) > self.agent.utility(self.left_coalition)

        self.f_in_left_coal = [other for other in left_coalition if other.utility(agent) > 0]
        self.f_out_left_coal = [other for other in left_coalition if other.utility(agent) < 0]
        self.f_in_joined_coal = [other for other in joined_coalition if other.utility(agent) > 0]
        self.f_out_joined_coal = [other for other in joined_coalition if other.utility(agent) < 0]

        self.num_voters_left_coal = len(self.f_in_left_coal) + len(self.f_out_left_coal)
        self.num_voters_joined_coal = len(self.f_in_joined_coal) + len(self.f_out_joined_coal)

        if self.num_voters_left_coal > 0:
            self.vote_out_left = Fraction(len(self.f_out_left_coal), self.num_voters_left_coal)
        else:
            self.vote_out_left = Fraction(1, 1)

        if self.num_voters_joined_coal > 0:
            self.vote_in_joined = Fraction(len(self.f_in_joined_coal), self.num_voters_joined_coal)
        else:
            self.vote_in_joined = Fraction(1, 1)

        if self.num_voters_left_coal + self.num_voters_joined_coal > 0:
            self.vote_joined = Fraction(len(self.f_out_left_coal) + len(self.f_in_joined_coal),
                                        self.num_voters_left_coal + self.num_voters_joined_coal)
        else:
            self.vote_joined = Fraction(1, 1)

    def reset(self, partition, agent, left_coalition, joined_coalition):
        # Allow for objects to be reinitialized, so that they can be reused for efficiency reasons
        self.__init__(partition, agent, left_coalition, joined_coalition)

    def is_deviation_type(self, stability_notion):
        if type(stability_notion) is StabilityEnum:
            stability_notion = StabilityNotion(stability_notion)

        if not self.is_nash:
            return False

        match stability_notion.notion:
            case StabilityEnum.Nash:
                return True
            case StabilityEnum.Individual:
                return len(self.f_out_joined_coal) == 0
            case StabilityEnum.Contractual:
                return len(self.f_in_left_coal) == 0
            case StabilityEnum.ContractualIndividual:
                return len(self.f_out_joined_coal) == 0 and len(self.f_in_left_coal) == 0
            case StabilityEnum.VoteIn:
                return self.vote_in_joined >= stability_notion.vote_in_quota
            case StabilityEnum.VoteOut:
                return self.vote_out_left >= stability_notion.vote_out_quota
            case StabilityEnum.VoteJoined:
                return self.vote_joined >= stability_notion.vote_joined_quota
            case StabilityEnum.VoteSeparate:
                return self.vote_in_joined >= stability_notion.vote_in_quota and self.vote_out_left >= stability_notion.vote_out_quota
            case _:
                raise ValueError(f'Stability notion {stability_notion} not supported')
