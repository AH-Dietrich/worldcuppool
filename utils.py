from datetime import datetime, timezone
from models import MatchInfo


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
