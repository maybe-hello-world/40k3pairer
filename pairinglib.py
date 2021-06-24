import dataclasses
import pandas as pd
from typing import Optional, Set


@dataclasses.dataclass
class PairingStatus:
    opa: Set[str]
    epa: Set[str]

    our_defender: Optional[str] = None
    enemy_defender: Optional[str] = None
    our_antidef: Optional[str] = None
    enemy_antidef: Optional[str] = None
    our_champion: Optional[str] = None
    enemy_champion: Optional[str] = None

    our_def_result: int = 0
    our_antidef_result: int = 0
    champ_result: int = 0

    def sum(self):
        return self.our_def_result + self.our_antidef_result + self.champ_result

    def copy(self):
        new_instance = dataclasses.replace(self)
        new_instance.opa = self.opa.copy()
        new_instance.epa = self.epa.copy()
        return new_instance

    def __str__(self):
        return f"""
        Available players of our team: {self.opa}
        Available players of enemy team: {self.epa}
        
        Our defender: {self.our_defender}
        Enemy's defender: {self.enemy_defender}
        
        Our anti-defender: {self.our_antidef}
        Enemy's anti-defender: {self.enemy_antidef}
        
        Our champion: {self.our_champion}
        Enemy's champion: {self.enemy_champion}
        
        Our defender's result: {self.our_defender}: {self.our_def_result} - {self.enemy_antidef}: {20 - self.our_def_result}
        Our anti-defender's result: {self.our_antidef}: {self.our_antidef_result} - {self.enemy_defender}: {20 - self.our_antidef_result}
        Our champion's result: {self.our_champion}: {self.champ_result} - {self.enemy_champion}: {20 - self.champ_result}
        Predicted sum of our scores: {self.sum()}  
        """


class PairResolver:
    def __init__(self, scores: pd.DataFrame):
        assert scores.shape == (3, 3)
        self.scores = scores

    def resolve_step1(self, current_status: PairingStatus) -> PairingStatus:
        return self.__our_step1(current_status)

    def resolve_step2(self, current_status: PairingStatus) -> PairingStatus:
        assert len(current_status.epa) == 2 and len(current_status.opa) == 2
        assert current_status.our_defender is not None and current_status.enemy_defender is not None
        return self.__our_step2(current_status)

    def __our_step1(self, status: PairingStatus):
        results = []
        for player in status.opa:
            ns = status.copy()
            ns.opa = ns.opa.difference({player})
            ns.our_defender = player
            results.append(self.__enemy_step1(ns))

        return max(results, key=lambda x: x.sum())

    def __enemy_step1(self, status: PairingStatus):
        results = []
        for player in status.epa:
            ns = status.copy()
            ns.epa = ns.epa.difference({player})
            ns.enemy_defender = player
            results.append(self.__our_step2(ns))

        return min(results, key=lambda x: x.sum())

    def __our_step2(self, status: PairingStatus):
        results = []
        for player in status.epa:
            ns = status.copy()
            ns.epa = ns.epa.difference({player})
            ns.enemy_antidef = player
            ns.enemy_champion = ns.epa.pop()
            ns.our_def_result = self.scores.loc[ns.our_defender][ns.enemy_antidef]
            results.append(self.__enemy_step2(ns))

        return max(results, key=lambda x: x.sum())

    def __enemy_step2(self, status: PairingStatus):
        results = []
        for player in status.opa:
            ns = status.copy()
            ns.opa = ns.opa.difference({player})
            ns.our_antidef = player
            ns.our_champion = ns.opa.pop()
            ns.our_antidef_result = self.scores.loc[ns.our_antidef][ns.enemy_defender]
            ns.champ_result = self.scores.loc[ns.our_champion][ns.enemy_champion]
            results.append(ns)

        return min(results, key=lambda x: x.sum())
