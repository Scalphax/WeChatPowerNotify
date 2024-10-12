from flask import Flask,request,jsonify,render_template
from config import token,get
import requests as req
import sqlite3 as sql
import time,threading

api_url = "https://wxpusher.zjiecode.com/api/send/message"
app = Flask(__name__)

processed_data = {
  "appToken": token,
  "content": "",
  "summary": "",
  "contentType": 2,
  "uids":[
  ], 
  "verifyPayType":0 
}

def open_sql():
    conn = sql.connect('elect.db')
    conn.row_factory = sql.Row
    return conn

def data_query(uid):
    conn = open_sql()
    roomid,used,money,alarm_kv,remain,timestamp = conn.execute('SELECT roomid,used,money,alarm,remain,timestamp FROM usr WHERE uid = ?',(uid,)).fetchone()
    buildname,areaname,dorm = conn.execute('SELECT buildname,areaname,dorm FROM kv WHERE roomid = ?',(roomid,)).fetchone()
    alarm,alarm_value = alarm_kv.split(':')
    alarm_type = lambda alarm: "元" if alarm == "m" else "度"
    processed_data['content'] = f"""<h1>当前状态</h1><br/>
                                <p>{buildname}{areaname}{dorm}</p><br/>
                                剩余电费: {money} 剩余电量: {remain} 电表记载电量: {used}<br/>
                                预警值: {alarm_value}{alarm_type(alarm)}<br/>
                                数据更新时间: {timestamp}"""
    req.post(api_url,json=processed_data,verify=False)

def refresh_data():
    conn = open_sql()
    rows = conn.execute('SELECT uid, roomid, alarm FROM usr').fetchall()
    for row in rows:
        raw_roomid = row[1]
        uid = row[0]
        roomid = raw_roomid[2:]
        up_dict = {
            "meterId":f"0311.{roomid}.1",
            "factorycode":"E035"
        }
        data = get("queryReserve",up_dict)
        conn.execute("""UPDATE usr  
                        SET money = ?, used = ?, remain = ?, timestamp = CURRENT_TIMESTAMP
                        WHERE uid = ?
                    """, (data['meterOverdue'],data['ZVlaue'],data['remainPower'],uid))
        alarm_type,alarm_value = row[2].split(':')
        at = lambda type: data['meterOverdue'] if type == "m" else data['remainPower']
        if float(alarm_value) >= float(at(alarm_type)):
            processed_data['uids'] = [uid,]
            processed_data['content'] = f"""<h1>低于预警线警告</h1><br/>
                            <p>您当前电费/电量低于预警线</p><br/>
                            详情请见下一条消息"""
            req.post(api_url,json=processed_data,verify=False)
            data_query(uid)
    conn.commit()
    time.sleep(600)
    refresh_data()

def wrong_code():
    processed_data['content'] = """<h1>指令错误</h1><br/>
                                    <p>目前支持 "#84800 setid 你的roomid" <br/>
                                             "#84800 check"</p>"""
    req.post(api_url,json=processed_data,verify=False)
    return '',400

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/callback",methods=['POST', 'GET'])
def command():
    data_json = request.json
    data = data_json['data']
    ctt = data['content']
    uid = data['uid']
    processed_data["uids"].append(uid)
    try:
        cmd = ctt.split(' ')[1]
    except:
        wrong_code()
    else:
        if cmd == "setid":
            try:
                roomid = ctt.split(' ')[2]
            except:
                wrong_code()
            else: #用户设置id
                try:
                    mid = f"0311.{roomid[2:]}.1"
                    up_dict = {
                        "factorycode" : "E035",
                        "meterId" : mid
                    }
                    user_data = get("queryReserve",up_dict)
                except:
                    processed_data['content'] = """<h1>roomid不存在</h1><br/>
                                    <p>请检查您的输入格式与roomid</p>"""
                    req.post(api_url,json=processed_data,verify=False)
                else:
                    conn = open_sql()
                    conn.execute("""INSERT OR REPLACE INTO usr (uid, roomid, used, remain, money, alarm, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)""",
                            (uid, roomid, user_data['ZVlaue'], user_data['remainPower'], user_data['meterOverdue'], "m:20"))
                    conn.commit()
                    buildname,areaname,dorm = conn.execute('SELECT buildname, areaname, dorm FROM kv WHERE roomid = ?',(roomid,)).fetchone()
                    processed_data['summary'] = f"提醒设置成功"
                    processed_data['content'] = f"""<h1>提醒设置成功</h1><br/>
                                                    <p>{buildname}{areaname}{dorm}<br/>
                                                    发送 "#84800 alarm 预警数值 rmb/kwh" 设定预警金额/度数(默认20元以下预警)</p>"""
                    req.post(api_url,json=processed_data,verify=False)
                    return '',200
        elif cmd == "alarm": #设置提醒限额
            try:
                alarm_type = lambda alarm: "m" if alarm == "rmb" else "w"
                alarm_kv = f"{alarm_type(ctt.split(' ')[3])}:{ctt.split(' ')[2]}"
                conn = open_sql()
                conn.execute('UPDATE usr SET alarm = ? WHERE uid = ?',(alarm_kv,uid,))
                conn.commit()
                processed_data['content'] = f"""<h1>预警线更改成功</h1><br/>
                                    <p>当前设置值为: {ctt.split(' ')[2]} {ctt.split(' ')[3]}</p>"""
                req.post(api_url,json=processed_data,verify=False)
                data_query(uid)
                return '',200
            except:
                wrong_code()
        elif cmd == "check":
            data_query(uid)
            return '',200
        else:
            wrong_code()
                    
@app.route('/areas', methods=['GET'])
def get_areas():
    conn = open_sql()
    areas = conn.execute('SELECT DISTINCT areaname FROM kv').fetchall()
    conn.close()
    return jsonify([dict(area) for area in areas])

@app.route("/builds",methods=['GET'])
def get_build():
    conn = open_sql()
    areaname = request.args.get('areaname')
    buildname_all = conn.execute('SELECT DISTINCT buildname from kv WHERE areaname = ?',(areaname,)).fetchall()
    conn.close()
    return jsonify([dict(build) for build in buildname_all])

@app.route('/rooms',methods=['GET'])
def get_room():
    conn = open_sql()
    areaname = request.args.get('areaname')
    buildname = request.args.get('buildname')
    rooms = conn.execute('SELECT roomid, dorm FROM kv WHERE areaname = ? AND buildname = ?', 
                         (areaname, buildname,)).fetchall()
    conn.close()
    return jsonify([dict(room) for room in rooms])

if __name__ == '__main__':
    loop_thread = threading.Thread(target=refresh_data)
    loop_thread.daemon = True  # 设置为守护线程，使得主线程退出时子线程也能结束
    loop_thread.start()

    # 运行 Flask 服务器
    app.run()