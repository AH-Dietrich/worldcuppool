from datetime import datetime, timezone

from models import MatchInfo, MatchMetadata, TeamInfo


def get_predictions_needed(match_ids: set[str], prediction_ids: set[str]) -> list[str]:
    to_be_predicted = []
    for match in match_ids:
        if match not in prediction_ids:
            to_be_predicted.append(match)
    return to_be_predicted


def is_match_completed(time: datetime, match_length: str) -> bool:
    return bool(
        (time + MatchInfo.MATCH_DURATION) > datetime.now(timezone.utc) and match_length
    )


def as_match_info(match_json: dict):
    home = as_team_info(match_json["home"])
    away = as_team_info(match_json["away"])
    metadata = as_match_metadata(match_json["data"])
    return MatchInfo(
        home=home,
        away=away,
        metadata=metadata,
        id=match_json["id"],
        is_completed=match_json["is_completed"],
    )


def as_team_info(team_json: dict):
    return TeamInfo(
        is_placeholder=False,
        score=team_json["score"],
        name=team_json["name"],
        pic_url=team_json["pic_url"],
        abbr=team_json["abbr"],
    )


def as_match_metadata(metadata_json: dict):
    return MatchMetadata(
        time=metadata_json["time"],
        stadium=metadata_json["stadium"],
        stage=metadata_json["stage"],
        match_length=metadata_json["match_length"],
    )
