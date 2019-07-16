import json
import time
import sys
from collections import Counter
#! /usr/bin/env python3
#SETUP
from typing import List, Any, Union

api_key = "" # Enter your own API key here!!
valid_servers = ['euw1', 'na1', 'eun1', 'br1', 'la1', 'la2', 'tr1', 'jp1', 'kr','ru','oc1']
try:
    import requests
except ImportError:
    print("\"requests\" module is not installed. \nPlease look at the Github instructions. -> https://github.com/YannickDC/league-friendCounter")
    quit(1)

if not api_key:
    if len(sys.argv) == 2:
        api_key = sys.argv[1]
    else:
        print("You forgot to change the api key.\nPlease look at the Github instructions. -> https://github.com/YannickDC/league-friendCounter")
        quit(1)
def get_all_match():
    account_name = None
    server = None
    while not account_name:
        try:
            account_name = input("What name would you like to lookup? >  ")
        except ValueError:
            print("Invalid input.")
    while not server in valid_servers:
        try:
            server = input("Enter a valid server: {} > ".format(valid_servers))
        except ValueError:
            print("Invalid input.")

    print('Trying to find summoner...')
    account_data = requests.get(
        "https://{}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{}?api_key={}".format(server, account_name,
                                                                                              api_key))
    if account_data.status_code == 404:
        print("Summoner \"{}\" does not exist!".format(account_name))
        quit(1)
    elif account_data.status_code == 403:
        print("Permission denied when requesting account data for summoner \"{}\"".format(account_name))
        quit(1)
    elif account_data.status_code != 200:
        print("Recieved error HTTP {} when requesting data for summoner \"{}\"".format(account_data.status_code,
                                                                                       account_name))
        print(account_data.url)
        quit(1)

    account_id = json.loads(account_data.text)["accountId"]
    print("Summoner has been found. Fetching match data. This might take a while...")
    the_final_result = []
    url = 'https://{}.api.riotgames.com/lol/match/v4/matchlists/by-account/{}?api_key={}'.format(server, account_id,
                                                                                                 api_key)
    response = requests.get(url)
    if response.status_code == 200:
        data = json.loads(response.text)
        if data is None:
            print("Error occurred!")
            return the_final_result
        matches = data['matches']
        counter = int(0)
        try:
            for m in matches:
                game_id = m['gameId']
                print("Progress: {}/{}".format(counter, (len(matches))))
                url = 'https://{}.api.riotgames.com/lol/match/v4/matches/{}?api_key={}'.format(server, game_id, api_key)
                response = requests.get(url)
                while response.status_code != 200:
                    print("API Rate limit has been hit, Sleeping for 10 seconds...")
                    time.sleep(10)
                    print("retrying...")
                    response = requests.get(url)

                if response.status_code == 200:
                    counter+=1
                    response_in_json = json.loads(response.text)
                    if "participantIdentities" in response_in_json:
                        participants = response_in_json['participantIdentities']
                        for each_participants in participants:
                            if "player" in each_participants:
                                summoner_name = each_participants["player"]["summonerName"]
                                the_final_result.append(summoner_name)
        except:
            print("Ran into an error chief. : ", response.status_code)

    # Time to load this in antother result set
    #We could remove the the player from the result set but the player could double check
    countResult = Counter(the_final_result)

    return countResult


if __name__ == "__main__":
    output = get_all_match()
    for k, v in output.most_common():
        print(k, v)
