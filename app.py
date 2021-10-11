import requests
import configparser
from flask import Flask, render_template
from db import get_db, create_table
from datetime import datetime
import time
from turbo_flask import Turbo
import threading


app = Flask(__name__)
turbo = Turbo(app)


@app.route('/')
def weather_home_page():
    baza = get_weather_conditions_form_db()
    return render_template('home.html', baza=baza)


@app.context_processor
def inject_load_data():
    data = get_actual_weather()
    temp = data['main']["temp"]
    temp_feels = data['main']["feels_like"]
    wind_speed = data["wind"]["speed"] * 3.6
    location = data["name"]
    day = data["dt"]
    load = [temp, temp_feels, wind_speed, day, location]
    print(load)
    # save the datas in database
    insert_weather_conditions_in_db(temp, temp_feels, wind_speed, day)

    return {'temp': int(load[0]), 'temp_feels': int(load[1]), 'wind_speed': int(load[2]),
            'date': load[3], 'location': load[4]}


@app.before_first_request
def before_first_request():
    threading.Thread(target=update_load).start()


def update_load():
    with app.app_context():
        i = 0
        while True:
            i += 1
            print(i)
            time.sleep(600)
            turbo.push(turbo.replace(render_template('loadavg-weather-conditions.html'), 'load'))


def get_weather_conditions_form_db():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'SELECT * FROM weather_conditions'
    cursor.execute(statement_sql)
    data = cursor.fetchall()
    db.close()
    return data


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

    app.run(host='0.0.0.0', port=8000, debug=False)
