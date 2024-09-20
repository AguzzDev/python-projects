from bs4 import BeautifulSoup
import requests
from utils.dictionaries import matchesFilterDictionary, cupsDictionary, leagueIconDictionary
from utils.db import save_db

BASE_URL = "https://www.transfermarkt.es/ticker/index/live"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
}
games = []


def main():
    response = requests.get(BASE_URL, headers=headers)
    if response.status_code != 200:
        return "Error"

    html = BeautifulSoup(response.text, 'html.parser')

    league_and_position = []
    end_games = "\n✅ --- Partidos terminados --- ✅\n"
    next_games = "\n🔜 --- Proximos partidos --- 🔜\n"
    live_games = "\n⚽ --- Partidos en vivo --- ⚽\n"

    all_leagues_or_competition = html.select(
        "#spieltagsbox div[class='kategorie']")
    for i, data in enumerate(all_leagues_or_competition):
        title = data.select_one("h2 a").text

        if title in matchesFilterDictionary:
            league_and_position.append({"pos": i, "title": title})

    tables = html.select("table.livescore")
    for item in league_and_position:
        league = item.get("title")
        pos = item.get("pos")
        table = tables[pos]
        rows = table.find("tbody").find_all("tr")
        i = 0

        for row in rows:
            local_team = row.select_one("td:nth-child(3) a").text.strip()
            local_team_img = row.select_one(
                "td:nth-child(3) a img")["data-src"] or None
            visitant_team = row.select_one("td:nth-child(5) a").text.strip()
            visitant_team_img = row.select_one(
                "td:nth-child(5) a img")["data-src"] or None
            result = row.select_one(
                "td:nth-child(4) a span")

            if league in cupsDictionary:
                league_text = f"\n🏆 {league}\n"
            else:
                league_text = f"\n{leagueIconDictionary.get(league)} {
                    league}\n"
            match_text = f"{local_team} - {result.text} - {visitant_team}\n"

            if "liveresult" in result.get("class", []):
                if i == 0:
                    live_games += league_text

                live_games += match_text
                status = "live"
            elif "finished" in result.get("class", []):
                if i == 0:
                    end_games += league_text

                end_games += match_text
                status = "finished"
            else:
                if i == 0:
                    next_games += league_text

                next_games += match_text
                status = "next"

            games.append({"localTeam": local_team, "localTeamImg": local_team_img, "result": result.text,
                         "visitantTeam": visitant_team, "visitantTeamImg": visitant_team_img, "league": league, "status": status})
            i += 1

    result_text = f"👋 Bienvenido, los partidos se muestran con el uso horario GMT+2\n{
        live_games}{next_games}{end_games}"

    save_db(games)
    return result_text


print(main())
