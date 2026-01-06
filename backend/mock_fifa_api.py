from flask import Flask
import json

app = Flask(__name__)


@app.get("/")
def get_mock_data():
    try:
        with open("mock_data.json", "r") as file:
            data = json.load(file)
            return data
    except:
        return ""


if __name__ == "__main__":
    app.run(port=3002)
