class User:
    def __init__(self,name:str,disc:str,elo:int=1000):
        self.name = name
        self.disc = disc
        self.elo = elo
        self.BO3_K = 24
        self.BO5_K = 32

    def __str__(self):
        return f"{self.name} | {round(self.elo,2)}"

    def match(self,other,won:bool,bo3:bool):
        self_expected = 1/(1+10**((other.elo-self.elo)/400))
        other_expected = 1-self_expected
        if bo3:
            self.elo += self.BO3_K*(int(won)-self_expected)
            other.elo += self.BO3_K*((int(not won))-other_expected)
        else:
            self.elo = self.elo + self.BO5_K*(int(won)-self_expected)
            other.elo = other.elo + self.BO5_K*(int(not won)-other_expected)

