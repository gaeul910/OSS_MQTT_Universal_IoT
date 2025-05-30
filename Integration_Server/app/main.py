from flask import Flask, render_template, request
import configparser
import pymysql
import sys
import time

app = Flask(__name__)

properties = configparser.ConfigParser()
properties.read("./config.properties")
MYSQL_HOST = properties["CONNECTION"]["host"]
MYSQL_PORT = int(properties["CONNECTION"]["port"])
MYSQL_USERNAME = properties["CONNECTION"]["user"]
MYSQL_PASSWORD = properties["CONNECTION"]["password"]
MYSQL_DB = properties["CONNECTION"]["db"]

try:
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USERNAME, passwd=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True)
except:
    sys.exit(3)

cursor = conn.cursor(pymysql.cursors.DictCursor)
# Please Note that responses could change when DB is linked.

def gen_id(table_name, id_name):
    try:
        allowed_table_name = ["clients", "eventlog", "locationlog", "userfavlocation", "userfavroute", "usernotifications", "users"]
        if table_name not in allowed_table_name:
            return -1
        query = "SELECT MAX(`{}`) AS highest_id FROM `{}`".format(id_name, table_name)
        cursor.execute(query)
        getdict = cursor.fetchone()
        ret_id = getdict['highest_id']
        if ret_id == 0:
            return 1
        if not ret_id and ret_id != 0:
            return 0
        return ret_id + 1
    except:
        return -1
        
@app.route("/location/logs", methods=['GET', 'POST', 'DELETE'])

def logs():
    if(request.method == 'GET'):
        dict_req = request.get_json()
        uid = dict_req["uid"]
        location_id = dict_req["location_id"]
        query = "SELECT id, uid, ST_AsText(coordinate) as coordinate, time FROM locationlog WHERE uid = %s AND id = %s"
        cursor.execute(query, (uid, location_id))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for uid: {} after location_id: {}".format(uid, location_id)
        return ret
        
    elif(request.method == 'POST'):
        try:
            get_dict = request.get_json()
            uid = get_dict["uid"]
            coordinate = get_dict["coordinate"]
            issued = get_dict["time"]
            location_id = gen_id("locationlog", "id")
            if location_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO locationlog VALUES (%s, %s, ST_GeomFromText(%s), %s)"
            ret = cursor.execute(query, (location_id, uid, coordinate, issued))
        except:
            return f"POST unsuccessful, {ret}"
        return "Success"

@app.route("/location/fav/point", methods=['GET', 'POST', 'DELETE'])

def point():
    if(request.method == 'GET'):
        dict_req = request.get_json()
        uid = dict_req["uid"]
        point_id = dict_req["point_id"]
        query = "SELECT id, uid, alias, ST_AsText(coordinate) as coordinate, status FROM userfavlocation WHERE uid = %s AND id = %s"
        cursor.execute(query, (uid, point_id))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for uid: {} after point_id: {}".format(uid, point_id)
        return ret
    
    elif(request.method == 'POST'):
        try:
            get_dict = request.get_json()
            uid = get_dict["uid"]
            coordinate = get_dict["coordinate"]
            alias = get_dict["alias"]
            status = get_dict["status"]
            point_id = gen_id("userfavlocation", "id")
            if point_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO userfavlocation VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)"
            ret = cursor.execute(query, (point_id, uid, alias, coordinate, status))
        except:
            return f"POST unsuccessful, {ret}"
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            point_id = get_dict["point_id"]
            uid = get_dict["uid"]
            query = "DELETE FROM userfavlocation WHERE id = %s AND uid = %s"
            ret = cursor.execute(query, (point_id, ))
        except:
            return "DELETE unsuccessful"
        return "Success"
    
@app.route("/location/fav/route", methods=['GET', 'POST', 'DELETE'])

def route():
    if(request.method == 'GET'):
        dict_req = request.get_json()
        startlocation_id = dict_req["startlocation_id"]
        query = "SELECT id, startlocation_id, endlocation_id, ST_AsText(route) AS route, status FROM userfavroute WHERE startlocation_id = %s"
        cursor.execute(query, (startlocation_id, ))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for startlocation_id: {}".format(startlocation_id)
        return ret
    
    elif(request.method == 'POST'):
        try:
            get_dict = request.get_json()
            route = get_dict["route"]
            startlocation_id = get_dict["startlocation_id"]
            endlocation_id = get_dict["endlocation_id"]
            status = get_dict["status"]
            route_id = gen_id("userfavroute", "id")
            if route_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO userfavroute VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)"
            ret = cursor.execute(query, (route_id, startlocation_id, endlocation_id, route, status))
        except:
            return f"POST unsuccessful, {ret}"
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            route_id = get_dict["route_id"]
            uid = get_dict["uid"]
            query = "DELETE FROM userfavroute WHERE id = %s AND uid = %s"
            ret = cursor.execute(query, (route_id, uid, ))
            return "Success"
        except:
            return "DELETE unsuccessful"

@app.route("/event/visits", methods=['GET'])

def visits():
    try:
        dict_req = request.get_json()
        location_id = dict_req["location_id"]
        lookup_days = dict_req["lookup_days"]
@app.route("/event/eventlogs", methods=['GET', 'POST', 'DELETE'])

def eventlogs():
    if(request.method == 'GET'):
        dict_req = request.get_json()
        event_id = dict_req["location_id"]
        query = "SELECT * FROM eventlog WHERE location_id = %s"
        cursor.execute(query, (event_id, ))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for event_id: {}".format(event_id)
        return ret
    
    elif(request.method == 'POST'):
        try:
            get_dict = request.get_json()
            log_id = get_dict["log_id"]
            event_id = get_dict["location_id"]
            about = get_dict["about"]
            event_id = gen_id("eventlog", "id")
            if event_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO eventlog VALUES (%s, %s, %s, %s)"
            ret = cursor.execute(query, (event_id, event_id, log_id, about, ))
        except:
            return f"POST unsuccessful, {ret}"
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            event_id = get_dict["event_id"]
            query = "DELETE FROM eventlog WHERE id = %s"
            ret = cursor.execute(query, (event_id, ))
            return "Success"
        except:
            return "DELETE unsuccessful"

@app.route("/notification/getnoti", methods=['GET'])

def getnoti():
    notification_id = request.headers["id"]
    notification_id = int(notification_id)
    try:
        cursor.execute("SELECT * FROM usernotifications WHERE id = %s", (notification_id,))
        ret = cursor.fetchall()
        
        if not ret:
            return "No notification found for {}".format(notification_id)
    except:
        return f"Error: {ret}"
    return ret
    
@app.route("/notification/postnoti", methods=['POST'])

def postnoti():
        uid = request.headers["uid"]
        dict_req = request.get_json()
        content = dict_req["content"]
        issue = dict_req["time"]
        about = dict_req["about"]
        uid = int(uid)
        query = "INSERT INTO usernotifications VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute("SELECT MAX(id) AS highest_id FROM usernotifications")
        getdict = cursor.fetchone()
        notification_id = getdict['highest_id']
        if not notification_id:
            notification_id = 0
        notification_id += 1

        try:
            cursor.execute(query, (notification_id, uid, content, issue, 0, about))
        except:
            return "Error"
        conn.commit()
        return "Success"

@app.route("/notification/sync", methods=['GET'])

def sync():
    uid = request.headers["uid"]
    uid = int(uid)
    try:
        cursor.execute("SELECT id FROM usernotifications WHERE uid = %s AND stat = %s", (uid, 0,))

        ret = cursor.fetchall()
        if not ret:
            return "No data to sync"
    except:
        return f"Error: {ret}"
    return ret

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)