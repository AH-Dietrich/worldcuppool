import json

with open("mock_data.json") as f:
    test = json.load(f)

    matches = test["Results"]

    for i in matches:
        print(i["StageName"][0]["Description"])
        print(i["PlaceHolderA"])
        print(i["PlaceHolderB"])
