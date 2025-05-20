from flask import Flask, render_template, request
import pymysql
import sys
import time

app = Flask(__name__)
MYSQL_HOST = "db"
MYSQL_PORT = 3306
MYSQL_USERNAME = "root"
MYSQL_PASSWORD = "defaultpassword1"
MYSQL_DB = "iot-db"
try:
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USERNAME, passwd=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True)
except:
    sys.exit(3)

cursor = conn.cursor(pymysql.cursors.DictCursor)
# Please Note that responses could change when DB is linked.

def gen_id(table_name, id_name):
    try:
        allowed_table_name = ["clients", "events", "locationlog", "userfavlocation", "userfavroute", "usernotifications", "users"]
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
        
@app.route("/location/logs", methods=['GET', 'POST'])

def logs():
    if(request.method == 'GET'):
        uid = request.args.get("uid", "str")
        if(uid == "sample-uid"):
            return render_template("location.json")
        return "Request by UID is still under development"
        
    elif(request.method == 'POST'):
        uid = request.args("uid", "str")
        jsonoutput = open("templates/locationforupload.json", "w")
        jsonoutput.write(request.data)
        return

@app.route("/location/fav/point", methods=['GET', 'POST'])

def point():
    if(request.method == 'GET'):
        uid = request.args.get("uid", "str")
        if(uid == "sample-uid"):
            return render_template("favpoint.json")
        return "Request by UID is still under development"
    
    elif(request.method == 'POST'):
        uid = request.args.get("uid", "str")
        jsonoutput = open("templates/favlocationforupload.json", "w")
        jsonoutput.write(request.data)
        return
    
@app.route("/location/fav/route", methods=['GET', 'POST'])

def route():
    if(request.method == 'GET'):
        uid = request.args.get("uid", "str")
        if(uid == "sample-uid"):
            return render_template("favroute.json")
        return "Request by UID is still under development"
    
    elif(request.method == 'POST'):
        uid = request.args.get("uid", "str")
        jsonoutput = open("templates/routelocationforupload.json", "w")
        jsonoutput.write(request.data)
        return
    
@app.route("/event/eventlogs", methods=['GET', 'POST'])

def eventlogs():
    if(request.method == 'GET'):
        uid = request.args.get("uid", "str")
        locationid = request.args.get("locationid", "str")
        if(uid == "sample-uid" and locationid == '1'):
            return render_template("event.json")
        return "Request by UID and Location ID is still under development"
    
    elif(request.method == 'POST'):
        uid = request.args.get("uid", "str")
        jsonoutput = open("templates/eventforupload.json", "w")
        jsonoutput.write(request.data)
        return
    
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