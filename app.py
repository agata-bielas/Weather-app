import requests
import configparser
from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def weather_home_page():
    api_key = get_api_key()
    data = get_actual_weather(api_key)
    temp = data["main"]["temp"]
    temp_feels = data["main"]["temp"]
    wind_speed = data["wind"]["speed"]
    location = data["name"]
    return render_template('home.html',
                           temp=temp, temp_feels=temp_feels,
                           wind_speed=wind_speed, location=location)


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']


def get_actual_weather(api_key):
    api_url = "http://api.openweathermap.org/data/2.5/weather?lat=35.88&lon=76.51&APPID={}&units=metric".format(api_key)
 #   print(api_url)
    response = requests.get(api_url)
    return response.json()


def get_foreseen_weather(api_key):
    api_url = "http://api.openweathermap.org/data/2.5/forecast?lat=35.88&lon=76.51&APPID={}&units=metric".format(api_key)
    response = requests.get(api_url)
    return response.json()


if __name__ == '__main__':
    # w terminalu widze wszystie dane ;)
    # print("Prognozowana pogoda")
    # print(get_foreseen_weather(get_api_key()))
    # print("Aktualna pogoda")
    # print(get_actual_weather(get_api_key()))
    app.run()

