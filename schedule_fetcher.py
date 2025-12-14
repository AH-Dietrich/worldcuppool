import requests

from datetime import datetime, timezone
from models import ScheduleInfo, TeamInfo, GameInfo, MatchData


class data_service:
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }
    URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idSeason=285023"

    @staticmethod
    def get_latest_schedule() -> ScheduleInfo:
        req = requests.get(data_service.URL, headers=data_service.HEADERS)
        matches_json = req.json()

        matches: list[GameInfo] = []

        for match in matches_json["Results"]:
            data = data_service._get_match_data(match)
            home, away = data_service._get_match_lineup(match)
            id = match.get("IdMatch")
            is_completed = data_service._is_match_completed(
                data.time, data.match_length
            )
            matches.append(GameInfo(home, away, data, id, is_completed))
        return ScheduleInfo(matches)

    @staticmethod
    def _get_match_data(match_json: dict) -> MatchData:
        time_string = match_json.get("Date", "")
        time = datetime.fromisoformat(time_string)
        stadium = match_json.get("Stadium", {}).get("Name", [])[0].get("Description")
        stage = match_json.get("StageName", [])[0].get("Description")
        match_length = match_json.get("MatchTime", "")

        return MatchData(time, stadium, stage, match_length)

    @staticmethod
    def _is_match_completed(time: datetime, match_length: str) -> bool:
        return bool(
            (time + GameInfo.MATCH_DURATION) > datetime.now(timezone.utc)
            and match_length
        )

    @staticmethod
    def _get_match_lineup(match_json: dict) -> tuple[TeamInfo, TeamInfo]:
        away_dict = match_json.get("Away", {})
        home_dict = match_json.get("Home", {})

        away_dict = away_dict or {}
        home_dict = home_dict or {}

        away = data_service._get_team_info(
            away_dict, match_json.get("PlaceHolderB", "NO")
        )
        home = data_service._get_team_info(
            home_dict, match_json.get("PlaceHolderA", "NO")
        )
        return (home, away)

    @staticmethod
    def _get_team_info(team_json: dict, placeholder_name: str = "N/A") -> TeamInfo:
        score = team_json.get("Score", 0)
        name = team_json.get("ShortClubName", placeholder_name)
        pic_url = team_json.get("PictureUrl", placeholder_name)
        abbr = team_json.get("Abbreviation", placeholder_name)

        pic_url = pic_url.format(format="sq", size="1")

        return TeamInfo(score or 0, name, pic_url, abbr)
