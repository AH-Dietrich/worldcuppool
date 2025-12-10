import datetime

class TeamInfo:
    def __init__(self, score: int, name: str, pic_url: str, abbr: str):
        self.score = score
        self.name = name
        self.pic_url = pic_url
        self.abbr = abbr

class GameInfo:
    def __init__(self, home: TeamInfo, away: TeamInfo, time: datetime.datetime):
        self.home = home
        self.away = away
        self.time = time
    def todict(self):
        return {'home': self.home.__dict__, 'away': self.away.__dict__, 'time': self.time}

class ScheduleInfo:
    def __init__(self, matches: list[GameInfo]):
        self.matches = matches