import curl_cffi as requests
from dataclasses import dataclass
import os
import time


STARTER_ID = 792100
PACKS_FOLDER = "./packets/"



@dataclass
class MatchData:
    id: int
    sport: str
    season: str
    slug: str
    url: str

@dataclass
class MatchStats:
    id: int

def get_info(id:int) -> MatchData:
    with  requests.Session() as session:
        session.headers = {
        "Host": "www.sofascore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": "https://www.sofascore.com/football/match/curacao-panama/odcsCqx",
        "X-Requested-With": "3c3e3f",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
        res = session.get(f"https://www.sofascore.com/api/v1/event/{id}",impersonate="chrome")

        if res.status_code != 200:
            print(f"Failed to fetch match info for ID {id}. Status code: {res.status_code}")
            return None
        data = res.json()

        sport = data["event"]["tournament"]["category"]["sport"]["name"]
        season = data["event"]["season"]["name"].replace("/", "-")
        slug = data["event"]["slug"]
        id_data = id
        url = f"https://www.sofascore.com/api/v1/event/{id}"

        return MatchData(id=id_data, sport=sport, season=season, slug=slug, url=url)


def get_match_data(m:MatchData):
    with requests.Session() as session:
        session.headers = {
        "Host": "www.sofascore.com",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:160.0) Gecko/20100101 Firefox/160.0",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Referer": f"https://www.sofascore.com/{m.sport}/{m.season}/{m.slug}/{m.id}",
        "X-Requested-With": "3c3e3f",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "Priority": "u=4",
        "Cache-Control": "max-age=0",
        "TE": "trailers",
    }
        res = session.get(f"https://www.sofascore.com/api/v1/event/{m.id}/statistics",impersonate="chrome")
        data = res.json()
        if "statistics" not in data:
            print(f"Statistics not found for match ID {m.id}")
            return None
        return str(data).replace("'", '"')  # Convert single quotes to double quotes for JSON compatibility

def create_packet(match_data: MatchData,stats:dict):
    packet_name = f"{match_data.sport}_{match_data.season}_{match_data.slug}"
    packet_path = os.path.join(PACKS_FOLDER, f"{packet_name}")
    packet_datafile = os.path.join(packet_path, "data.yml")
    packet_stats = os.path.join(packet_path, "stats.json")
    os.makedirs(packet_path, exist_ok=True)
    with open(packet_datafile, "w") as f:
        f.write(f"id: {match_data.id}\nsport: {match_data.sport}\nseason: {match_data.season}\nslug: {match_data.slug}\nurl: {match_data.url}\n")
    with open(packet_stats, "w") as f:
        f.write(str(stats))
    return 0



def do_cycle(id:int):
    match_data = get_info(id)
    if match_data is None:
        print(f"Skipping match ID {id} due to failed info retrieval.")
        return
    stats = get_match_data(match_data)
    if stats is None:
        print(f"Skipping match DATA")
    create_packet(match_data, "")
    print(f"Successfully processed match ID {id} and created packet.")


def ketchup():

    if os.path.exists("last"):
        with open("last","r") as f:
            print(f.readlines())
            if f.read().strip() == "":
                last_id = STARTER_ID
            else:
                last_id = int(f.readlines()[0].strip())
            return last_id
    else:
        return STARTER_ID

def start():
    starting = ketchup()
    lead = starting
    while True:
        try:
            print(f"Processing match ID: {lead}")
            do_cycle(lead)
            with open("last","w") as f:
                f.write(str(lead).strip())
            lead += 1
        except Exception as e:
            print(f"Error processing match ID {lead}: {e}")
        time.sleep(1)


start()