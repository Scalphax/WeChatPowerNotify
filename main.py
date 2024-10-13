from flask import Flask,request,jsonify
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import sqlite3 as sql

api_url = "https://wxpusher.zjiecode.com/api/send/message"
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

utc8 = timezone(timedelta(hours=8))
def current_time():
    current_time_utc8 = datetime.now(utc8)
    current_time = current_time_utc8.strftime("%Y-%m-%d %H:%M:%S")
    return current_time


def open_sql():
    conn = sql.connect('elect.db')
    conn.row_factory = sql.Row
    return conn
                
@app.route('/areas', methods=['POST'])
def get_areas():
    conn = open_sql()
    areas = conn.execute('SELECT DISTINCT areaname FROM kv').fetchall()
    conn.close()
    return jsonify([dict(area) for area in areas])

@app.route("/builds", methods=['POST'])
def get_build():
    conn = open_sql()
    data = request.get_json()
    areaname = data.get('areaname')
    buildname_all = conn.execute('SELECT DISTINCT buildname from kv WHERE areaname = ?', (areaname,)).fetchall()
    conn.close()
    return jsonify([dict(build) for build in buildname_all])

@app.route('/rooms', methods=['POST'])
def get_room():
    conn = open_sql()
    data = request.get_json()
    areaname = data.get('areaname')
    buildname = data.get('buildname')
    rooms = conn.execute('SELECT roomid, dorm FROM kv WHERE areaname = ? AND buildname = ?', 
                         (areaname, buildname,)).fetchall()
    conn.close()
    return jsonify([dict(room) for room in rooms])

if __name__ == '__main__':
    # 运行 Flask 服务器
    app.run(host='0.0.0.0', port=16850)