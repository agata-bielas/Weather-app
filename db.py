import sqlite3

DATABASE_NAME = "weather.sqlite3"


def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn


def create_table():
    db = get_db()
    cursor = db.cursor()
    statement_sql = 'CREATE TABLE IF NOT EXISTS weather_conditions(' \
                    'id INTEGER PRIMARY KEY AUTOINCREMENT, ' \
                    'temp REAL, ' \
                    'temp_feels_like REAL, ' \
                    'wind_speed REAL, ' \
                    'data INT)'

    cursor.execute(statement_sql)
    db.close()
