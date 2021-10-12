import requests
import configparser
from flask import Flask, render_template, request, redirect, url_for
from db import get_db, create_table
from datetime import datetime
import time
from turbo_flask import Turbo
import threading
import pandas as pd
import json
import plotly
import plotly.express as px

app = Flask(__name__)
turbo = Turbo(app)


@app.route('/', methods=['POST', 'GET'])
def weather_home_page():
    if request.method == 'POST':
        value = request.form['temp']
        return redirect(url_for("result", valu=value))
    elif request.method == "GET":
        df = get_data_for_forecast_weather_graph()
        fig = px.line(df, x="Time Forecast", y="Temperatur")

        graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('home.html', graphJSON=graphjson)


def get_data_for_forecast_weather_graph():
    key_api = get_api_key()
    get_data = get_foreseen_weather(key_api)
    time_forecast = [get_data["list"][i]["dt_txt"] for i in range(0, 39)]
    temp = [get_data["list"][i]["main"]["temp"] for i in range(0, 39)]

    df = pd.DataFrame(data={
        "Time Forecast": time_forecast,
        "Temperatur": temp
    })
    return df


@app.route('/<valu>')
def result(valu):
    get_data = 0
    text = ""
    if valu == 'min':
        get_data = get_min_temperature_from_db()
        text = "Minimalna temperatura"
    elif valu == 'max':
        get_data = get_max_temperature_from_db()
        text = "Maksymalna temperatura"
    elif valu == 'avg':
        get_data = get_avg_temperature_from_db()
        text = "Średnia temperatura"

    return render_template('results.html', description=text, data=get_data)


@app.context_processor
def inject_load_data():
    data = get_actual_weather()
    temp = data['main']["temp"]
    temp_feels = data['main']["feels_like"]
    wind_speed = data["wind"]["speed"] * 3.6
    location = data["name"]
    day = data["dt"]
    load = [temp, temp_feels, wind_speed, day, location]
    # save the datas in database
    insert_weather_conditions_in_db(temp, temp_feels, wind_speed, day)

    return {'temp': int(load[0]), 'temp_feels': int(load[1]), 'wind_speed': int(load[2]),
            'date': datetime.fromtimestamp(load[3]).strftime("%H:%M %A %d/%m/%Y"), 'location': load[4]}


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        while True:
            time.sleep(600)
            turbo.push(turbo.replace(render_template('load-weather-conditions.html'), 'load'))


def get_weather_conditions_form_db():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT * FROM weather_conditions'
    cursor.execute(statement_sql)
    data = cursor.fetchall()
    db.close()
    return data


def get_min_temperature_from_db():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT MIN(temp) From weather_conditions'
    cursor.execute(statement_sql)
    # Fetchall() give a list of tuples. Min temp is only one value, that return min_temp[0][0].
    min_temp = cursor.fetchall()
    db.close()
    return min_temp[0][0]


def get_max_temperature_from_db():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT MAX(temp) From weather_conditions'
    cursor.execute(statement_sql)
    max_temp = cursor.fetchall()
    db.close()
    # Fetchall() give a list of tuples. Max temp is only one value, that return max_temp[0][0].
    return max_temp[0][0]


def get_avg_temperature_from_db():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT AVG(temp) From weather_conditions'
    cursor.execute(statement_sql)
    avg_temp = cursor.fetchall()
    db.close()
    # Fetchall() give a list of tuples. Avg temp is only one value, that return avg_temp[0][0].
    return avg_temp[0][0]


def insert_weather_conditions_in_db(temp, temp_feels_like, wind_speed, data):
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'INSERT INTO weather_conditions(' \
                    'temp, temp_feels_like, wind_speed, data) ' \
                    'VALUES(?, ?, ?, ?)'
    cursor.execute(statement_sql, [temp, temp_feels_like, wind_speed, data])
    db.commit()
    db.close()
    return True


def get_api_key():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['openweathermap']['api']


def get_actual_weather():
    """
    Function get the actual weather from openweathermap.org for the K2
    """
    api_key = get_api_key()
    api_url = "http://api.openweathermap.org/data/2.5/weather?lat=35.88&lon=76.51&APPID={}&units=metric".format(api_key)
    response = requests.get(api_url)
    return response.json()


def get_foreseen_weather(api_key):
    """
    Function get the forecast weather from openweathermap.org for the K2
    :param api_key:
    :return:
    """
    api_url = "http://api.openweathermap.org/data/2.5/forecast?lat=35.88&lon=76.51&APPID={}&units=metric"
    response = requests.get(api_url.format(api_key))
    return response.json()


if __name__ == '__main__':
    """
        Create table in database db.sqlite3
    """
    create_table()

    app.run(host='0.0.0.0', port=8000, debug=True)
