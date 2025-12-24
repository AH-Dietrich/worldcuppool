from datetime import datetime, timezone

import requests

import utils
from models import MatchInfo, MatchMetadata, ScheduleInfo, TeamInfo


class data_service:
    HEADERS = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
    }
    URL = "https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idSeason=285023"
    # URL = "localhost:3002"

    @staticmethod
    def get_latest_schedule() -> ScheduleInfo:
        req = requests.get(data_service.URL, headers=data_service.HEADERS)
        matches_json = req.json()

        matches: list[MatchInfo] = []

        for match in matches_json["Results"]:
            matches.append(data_service._populate_match_info(match))

        return ScheduleInfo(matches)

    @staticmethod
    def _populate_match_info(match_json: dict) -> MatchInfo:
        data = data_service._get_match_metadata(match_json)
        home, away = data_service._get_match_lineup(match_json)
        id = match_json.get("IdMatch", "")
        is_completed = utils.is_match_completed(data.time, data.match_length)

        return MatchInfo(home, away, data, id, is_completed)

    @staticmethod
    def _get_match_metadata(match_json: dict) -> MatchMetadata:
        time_string = match_json.get("Date", "")
        time = datetime.fromisoformat(time_string)
        stadium = match_json.get("Stadium", {}).get("Name", [])[0].get("Description")
        stage = match_json.get("StageName", [])[0].get("Description")
        match_length = match_json.get("MatchTime", "")

        return MatchMetadata(time, stadium, stage, match_length)

    @staticmethod
    def _get_match_lineup(match_json: dict) -> tuple[TeamInfo, TeamInfo]:
        away_dict = match_json.get("Away")
        home_dict = match_json.get("Home")

        away = data_service._get_team_info(away_dict) if away_dict else TeamInfo()
        home = data_service._get_team_info(home_dict) if home_dict else TeamInfo()

        return (home, away)

    @staticmethod
    def _get_team_info(team_json: dict) -> TeamInfo:
        score = team_json.get("Score", 0)
        name = team_json.get("ShortClubName", "")
        abbr = team_json.get("Abbreviation", "")

        pic_url = team_json.get("PictureUrl", "")
        pic_url = pic_url.format(format="sq", size="1")

        return TeamInfo(False, score or 0, name, pic_url, abbr)
