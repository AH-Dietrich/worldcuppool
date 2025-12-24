import datetime
from collections import defaultdict
from enum import Enum

SCHEDULE_COLLECTION = "schedule2026_test"
PREDICTION_COLLECTION = "2026_predictions"
USER_COLLECTION = "2026_users"


class MatchPredictionVariant(Enum):
    PRECISE = 0
    GENERAL = 1


class TeamInfo:
    def __init__(
        self,
        is_placeholder: bool = True,
        score: int = 0,
        name: str = "",
        pic_url: str = "",
        abbr: str = "",
    ):
        self.is_placeholder = is_placeholder
        self.score = score
        self.name = name
        self.pic_url = pic_url
        self.abbr = abbr


class MatchMetadata:
    def __init__(
        self,
        time: datetime.datetime,
        stadium: str,
        stage: str,
        match_length: str,
    ):
        self.time = time
        self.stadium = stadium
        self.stage = stage
        self.match_length = match_length


class MatchInfo:
    MATCH_DURATION = datetime.timedelta(hours=1, minutes=30)

    def __init__(
        self,
        home: TeamInfo,
        away: TeamInfo,
        metadata: MatchMetadata,
        id: str,
        is_completed: bool,
    ):
        self.home = home
        self.away = away
        self.data = metadata
        self.id = id
        self.is_completed = is_completed

    def todict(self):
        return {
            "home": self.home.__dict__,
            "away": self.away.__dict__,
            "data": self.data.__dict__,
            "id": self.id,
            "is_completed": self.is_completed,
        }


class ScheduleInfo:
    def __init__(self, matches: list[MatchInfo]):
        self.matches = matches


class MatchPrediction:
    def __init__(
        self,
        home_score: int,
        away_score: int,
        match_id: str,
        variant: MatchPredictionVariant,
    ):
        self.home_score = home_score
        self.away_score = away_score
        self.match_id = match_id
        self.variant = variant.name

    def to_dict(self):
        return {
            "home_score": self.home_score,
            "away_score": self.away_score,
            "variant": self.variant,
        }


class User:
    def __init__(self) -> None:
        self.user_id: str
        self.predictions: dict[str, MatchPrediction] = defaultdict()

    def add_prediction(self, prediction: MatchPrediction):
        self.predictions[prediction.match_id] = prediction

    def get_prediction(self, match_id: str) -> MatchPrediction | None:
        return self.predictions.get(match_id)

    def update_user_score(self, schedule: ScheduleInfo):
        for match in schedule.matches:
            if match.data.time and match.data.time < datetime.datetime.now():
                match_prediction = self.predictions[match.id]
                self.user_score += self._calculate_variant_score(
                    match, match_prediction
                )

    def _calculate_variant_score(
        self, match: MatchInfo, match_prediction: MatchPrediction
    ):
        return match_prediction.home_score == match.home.score
