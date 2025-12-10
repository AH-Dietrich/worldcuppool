import requests

from models import ScheduleInfo, TeamInfo, GameInfo

class data_service:
  headers = {'Accept': 'application/json, text/plain, */*',
          'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'}
  url = 'https://api.fifa.com/api/v3/calendar/matches?language=en&count=500&idSeason=285023'

  @staticmethod
  def get_latest_schedule() -> ScheduleInfo:
    req = requests.get(data_service.url, headers=data_service.headers)
    matches_json = req.json()

    matches: list[GameInfo] = []

    for match in matches_json['Results']:
        time = match.get('Date')
        home, away = data_service._get_match_lineup(match)
        matches.append(GameInfo(home, away, time))
    return ScheduleInfo(matches)

  @staticmethod
  def _get_match_lineup(match_json: dict) -> tuple[TeamInfo, TeamInfo]:
      away_dict = match_json.get('Away', {})
      home_dict = match_json.get('Home', {})
      
      away_dict = away_dict or {}
      home_dict = home_dict or {}
      
      away = data_service._get_team_info(away_dict, match_json.get('PlaceHolderB', 'NO'))
      home = data_service._get_team_info(home_dict, match_json.get('PlaceHolderA', 'NO'))
      return (home, away)

  @staticmethod
  def _get_team_info(team_json: dict, placeholder_name: str = 'N/A') -> TeamInfo:
      score = team_json.get('Score', 0)
      name = team_json.get('ShortClubName', placeholder_name)
      pic_url = team_json.get('PictureUrl', placeholder_name)
      abbr = team_json.get('Abbreviation', placeholder_name)

      return TeamInfo(score or 0, name, pic_url, abbr)
