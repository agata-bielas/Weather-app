import requests
import configparser
from flask import Flask, render_template
from db import get_db, create_table
import time

app = Flask(__name__)


@app.route('/')
def weather_home_page():
    api_key = get_api_key()
    data = get_actual_weather(api_key)
    temp = data["main"]["temp"]
    temp_feels = data["main"]["feels_like"]
    wind_speed = data["wind"]["speed"]*3.6
    location = data["name"]
    day = data["dt"]
    print(day) # dzien ma byc w formacie "2021-10-8 14:00:00" lub innym chce to zapisac do bazydanych
    insert_weather_conditions_in_db(temp, temp_feels, wind_speed, day)
    data_from_db = get_weather_conditions_form_db()
    return render_template('home.html',
                           temp=temp, temp_feels=temp_feels,
                           wind_speed=wind_speed, location=location, database=data_from_db)


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


def get_actual_weather(api_key):
    """
    Function get the actual weather from openweathermap.org for the K2
    :param api_key:
    :return: response.json()
    """
    api_url = "http://api.openweathermap.org/data/2.5/weather?lat=35.88&lon=76.51&APPID={}&units=metric".format(api_key)
    response = requests.get(api_url)
    return response.json()


def get_foreseen_weather(api_key):
    api_url = "http://api.openweathermap.org/data/2.5/forecast?lat=35.88&lon=76.51&APPID={}&units=metric".format(api_key)
    response = requests.get(api_url)
    return response.json()


if __name__ == '__main__':
    """
        Create table in database db.sqlid3
    """
    create_table()

    app.run()


