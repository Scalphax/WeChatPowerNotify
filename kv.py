from config import get
import sqlite3,json,time

conn = sqlite3.connect('elect.db')
cursor = conn.cursor()

mode = "allrefresh"

up_dict = {
    'factorycode':'E035'
    }

areas = get('getAreaInfo',up_dict)['areaList']

if mode == "append":
    cursor.execute("SELECT * FROM kv ORDER BY timestamp DESC LIMIT 1")
    cache = open("cache","r",encoding='utf-8')
    last = cursor.fetchone()
    temp = list(last)
    last = temp
    up_dict = {
        'areaid':last[4],
        'factorycode':'E035'
    }
    buildings = get('queryBuildList',up_dict)['buildList']
    floorbegin = (json.load(cache)['lastfloor'] - 1)
    buildbegin = buildings.index(f"{last[1]}@{last[2]}")
    areasbegin = areas.index(f"{last[4]}@{last[5]}")
    
elif mode == "allrefresh":
    cursor.execute("DELETE FROM kv")
    conn.commit()
    floorbegin = None
    buildbegin = None
    areasbegin = None

# getAreaInfo => 获取校区列表,
# queryBuildList => 获取楼栋列表,
# queryFloorList => 获取楼层列表,
# getRoomInfo => 获取寝室列表,
# queryRoomElec => 获取寝室mid,
# queryReserve => 获取寝室电费信息

for area in areas[areasbegin:]:
    areaid,areaname = area.split('@')
    up_dict = {
        'areaid':areaid,
        'factorycode':'E035'
    }
    try:
        buildings = get('queryBuildList',up_dict)['buildList']
    except:
        print(f"获取建筑列表失败,区域{areaname}")
    for building in buildings[buildbegin:]:
        buildid,buildname = building.split('@')
        up_dict = {
            'areaid':areaid,
            'buildid':buildid,
            'factorycode':'E035'
        }
        try:
            floors = get('queryFloorList',up_dict)['floorList']
        except:
            print(f"获取楼层列表失败,建筑{buildname}")
        for floor in floors[floorbegin:]:
            try:
                up_dict = {
                    'buildid':buildid,
                    'floorid':floor,
                    'factorycode':'E035'
                }
                rooms = get("getRoomInfo",up_dict)["roomList"]
            except:
                print(f"W:获取楼层房间列表失败,位于{buildname},{floor}层")
            else:
                for room in rooms:
                    roomid,room_part = room.split("@")
                    try:
                        building2,dorm = room_part.split('-')
                    except ValueError:
                        print(f"W:非标准命名房间,位于{buildname},{room_part}")
                        dorm = room_part
                    cursor.execute(f"INSERT OR REPLACE INTO kv (areaid,buildid,roomid,areaname,buildname,dorm,timestamp) VALUES ('{areaid}', '{buildid}',  '{roomid}', '{areaname}', '{buildname}', '{dorm}', CURRENT_TIMESTAMP)")

            conn.commit()
            time.sleep(0.5)
        floorbegin = None
    buildbegin = None


conn.commit()
conn.close()
