import requests
from base64 import b64encode as e
import urllib3
import re
import subprocess
import time
import webbrowser
from colorama import Fore, Style, init

urllib3.disable_warnings()
init(convert=True)


class taiwanhack:
    def __init__(self) -> None:
        self.data = self.get_wmic_info()
        self.auth = e(("riot:" + self.data["client_auth"]).encode()).decode()
        self.riot_auth = e(("riot:" + self.data["riot_auth"]).encode()).decode()

    def get_wmic_info(self):
        res = str(
            subprocess.Popen(
                [
                    "wmic",
                    "process",
                    "where",
                    "name='LeagueClientUx.exe'",
                    "GET",
                    "commandline",
                ],
                shell=True,
                stdout=subprocess.PIPE,
            ).communicate()[0]
        )
        data = {
            "client_port": re.findall("--app-port=([0-9]*)", res)[0],
            "riot_port": re.findall("--riotclient-app-port=([0-9]*)", res)[0],
            "client_auth": re.findall("--remoting-auth-token=([\w-]*)", res)[0],
            "riot_auth": re.findall("--riotclient-auth-token=([\w-]*)", res)[0],
        }
        return data

    def get_region(self):
        r = requests.get(
            f"https://127.0.0.1:{self.data['client_port']}/lol-rso-auth/v1/authorization",
            headers={"Authorization": "Basic " + self.auth},
            verify=False,
        )
        return r.json()["currentPlatformId"]

    def get_summoner_display_name(self):
        r = requests.get(
            f"https://127.0.0.1:{self.data['client_port']}/lol-summoner/v1/current-summoner",
            headers={"Authorization": "Basic " + self.auth},
            verify=False,
        )
        return r.json()["displayName"]

    def get_gamestate(self):
        r = requests.get(
            f"https://127.0.0.1:{self.data['client_port']}/lol-gameflow/v1/gameflow-phase",
            headers={"Authorization": "Basic " + self.auth},
            verify=False,
        )
        return r.json()

    def get_participants(self):
        if self.get_gamestate() == "ChampSelect":
            r = requests.get(
                f"https://127.0.0.1:{self.data['riot_port']}/chat/v5/participants/champ-select",
                headers={"Authorization": "Basic " + self.riot_auth},
                verify=False,
            )
            if len(r.json()["participants"]) > 0:
                participants = []
                for p in r.json()["participants"]:
                    participants.append(p["name"])
                return participants
            else:
                print(r.json())
                print(
                    "Loading Champ Select... (5 sec)... If your chat doesn't load, close, connect to the chat and re-open the program"
                )
                time.sleep(5)
                return self.get_participants()

        else:
            print("Waiting for champ select (15 sec)")
            time.sleep(15)
            return self.get_participants()

    def open_multigg(self, participant_list):
        print(participant_list)
        string = "%2C".join(participant_list)
        url = f"https://www.op.gg/multisearch/euw?summoners={string}"
        webbrowser.open(url, new=2, autoraise=True)


if __name__ == "__main__":
    a = taiwanhack()
    print(
        Fore.LIGHTMAGENTA_EX
        + Style.BRIGHT
        + "Made By Gumi (https://github.com/gvmii) and Aniell4 (https://github.com/Aniell4)"
        + Style.RESET_ALL
    )
    print("Your summoner display name: " + a.get_summoner_display_name())
    a.open_multigg(a.get_participants())
