from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from difflib import SequenceMatcher

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    user = request.form["country"].title()
    response = requests.get("https://scrapethissite.com/pages/simple/")
    soup = BeautifulSoup(response.content, "html.parser")

    capital_name = None
    countries = soup.find_all("div", class_="col-md-4 country")
    for country in countries:
        name = country.find("h3", class_="country-name")
        if user == name.get_text(strip=True):
            capital_name = country.find("span", class_="country-capital").get_text(
                strip=True
            )
            break  # stop looping once found

    if not capital_name:
        return render_template("result.html", error="Country not found!")

    city_name = capital_name
    city_wttr = f"https://wttr.in/{city_name}?format=j1"
    try:
        req_get = requests.get(city_wttr)
        weather_data = req_get.json()
        area_name = weather_data["nearest_area"][0]["areaName"][0]["value"]
        ratio = SequenceMatcher(None, city_name, area_name).ratio()

        if ratio < 0.5:
            return render_template("result.html", error="City not found!")

        else:

            current_wttr = weather_data["current_condition"]
            current = current_wttr[0]
            condition = current["weatherDesc"][0]["value"]
            temperature = current["temp_C"]
            humidity = current["humidity"]
            wind_speed = current["windspeedKmph"]
            return render_template(
                "result.html",
                country=user,
                capital=capital_name,
                condition=condition,
                temperature=temperature,
                humidity=humidity,
                wind_speed=wind_speed,
            )
    except requests.exceptions.RequestException as e:
        return "something went wrong!"


if __name__ == "__name__":
    app.run(debug=True)
