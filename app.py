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
    """
    Loading home.html to the webpage as method GET.
    After method POST redirecting to function result with parameter valu (min, max, avg).
    :return: graph forecast weather
    """
    if request.method == 'POST':
        value = request.form['temp']
        return redirect(url_for("result", valu=value))
    elif request.method == "GET":
        return render_template('home.html', graphJSON=get_graph_for_forecast_weather())


def get_graph_for_forecast_weather():
    """
    Loading data from api. Assigning list to params (time_forecast, temp).
    Creating data frame for graph.
    Makeing plotly fig into json object.
    :return: graphjson - graph with forecast weather
    """
    key_api = get_api_key()
    get_data = get_foreseen_weather(key_api)
    time_forecast = [get_data["list"][i]["dt_txt"] for i in range(0, 39)]
    temp = [get_data["list"][i]["main"]["temp"] for i in range(0, 39)]

    df = pd.DataFrame(data={
        "Date": time_forecast,
        "Temperature°C": temp
    })

    fig = px.line(df, x="Date", y="Temperature°C")

    fig.update_layout(
        margin=dict(l=5, r=10, t=40, b=5)
    )
    fig.update_traces(
        mode='lines+markers'
    )
    graphjson = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphjson


@app.route('/<valu>')
def result(valu):
    """
    Function sent the extra data to web application.
    :param valu: is min, max or avg
    :return: get_data: is minimal temperature, maximal temperature or average temperature depends of param valu
    :return: graph forecast weather
    """
    get_data = 0
    text = ""
    if valu == 'min':
        get_data = get_min_temperature_from_db()
        text = "Minimal temperature"
    elif valu == 'max':
        get_data = get_max_temperature_from_db()
        text = "Maximal temperature"
    elif valu == 'avg':
        get_data = get_avg_temperature_from_db()
        text = "Average temperature"

    return render_template('results.html',
                           description=text,
                           data=round(get_data),
                           graphJSON=get_graph_for_forecast_weather())


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
    insert_weather_conditions_in_db(temp, temp_feels, round(wind_speed, 2), day)

    return {'temp': round(load[0]),
            'temp_feels': round(load[1]),
            'wind_speed': round(load[2]),
            'date': datetime.fromtimestamp(load[3]).strftime("%A %d/%m/%Y"),
            'location': load[4]}


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        while True:
            # Datas from openweadtermap.org are update every 10 minuts.
            # turbo in a load send new datas to templates and wait 5 minuts
            time.sleep(300)
            turbo.push(turbo.replace(render_template('load-weather-conditions.html'), 'load'))


def get_all_weather_conditions_from_db():
    """
    Query to database to get all data saved in there.
    :return: list of tuples
    """
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT * FROM weather_conditions'
    cursor.execute(statement_sql)
    data = cursor.fetchall()
    # for param in data:
    #     print(param[0], param[1], param[2], param[3], datetime.fromtimestamp(param[4]).strftime("%H:%m %A %d/%m/%Y"))
    db.close()
    return data


def get_min_temperature_from_db():
    """
    Query to database to get minimum temperature
    :return: minimum temperature
    """
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT MIN(temp) From weather_conditions'
    cursor.execute(statement_sql)
    min_temp = cursor.fetchall()
    db.close()
    # Fetchall() give a list of tuples. Min temp is only one value, that return min_temp[0][0].
    return min_temp[0][0]


def get_max_temperature_from_db():
    """
    Query to database to get maximum temperature
    :return: maximum temperature
    """
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT MAX(temp) From weather_conditions'
    cursor.execute(statement_sql)
    max_temp = cursor.fetchall()
    db.close()
    # Fetchall() give a list of tuples. Max temp is only one value, that return max_temp[0][0].
    return max_temp[0][0]


def get_avg_temperature_from_db():
    """
    Query to database to get average of temperature
    :return: avarege of temperatur
    """
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT AVG(temp) From weather_conditions'
    cursor.execute(statement_sql)
    avg_temp = cursor.fetchall()
    db.close()
    # Fetchall() give a list of tuples. Avg temp is only one value, that return avg_temp[0][0].
    return avg_temp[0][0]


def insert_weather_conditions_in_db(temp, temp_feels_like, wind_speed, data):
    """
    Function save params to database.
    :param temp:
    :param temp_feels_like:
    :param wind_speed:
    :param data:
    :return: True
    """
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
    """
    Function read the api_key from file config.ini.
    Return api_key with is nesesary to get the data from page openweathermap.org
    :return: api_key
    """
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
    # Create table in database db.sqlite3
    create_table()
    # Run the application
    app.run(host='0.0.0.0', port=8000, debug=True)
