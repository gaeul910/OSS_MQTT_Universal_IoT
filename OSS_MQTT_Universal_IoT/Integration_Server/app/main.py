from flask import Flask, render_template, request
from mqtt_module import MQTTClient
import mqtt_module
import configparser
import pymysql
import sys
import socket
import time
import secrets
import random
from flask_bcrypt import Bcrypt

app = Flask(__name__)
bcrypt = Bcrypt(app)

properties = configparser.ConfigParser()
properties.read("./config.properties")
MYSQL_HOST = properties["CONNECTION"]["host"]
MYSQL_PORT = int(properties["CONNECTION"]["port"])
MYSQL_USERNAME = properties["CONNECTION"]["user"]
MYSQL_PASSWORD = properties["CONNECTION"]["password"]
MYSQL_DB = properties["CONNECTION"]["db"]

services = {}
services_domain = properties["SERVICES"]
services_id = properties["SERVICES_ID"]

# Parse services into dictionary
for key in services_domain.keys():
    services[key] = {"service_domain": services_domain[key], "service_id": services_id[key]}


try:
    conn = pymysql.connect(host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USERNAME, passwd=MYSQL_PASSWORD, database=MYSQL_DB, autocommit=True)
except:
    sys.exit(3)

cursor = conn.cursor(pymysql.cursors.DictCursor)
# Please Note that responses could change when DB is linked.

properties.read("./mqtt.properties")
MQTT_BROKER_HOST = properties["BROKER"]["host"]
try:
    mqtt_client = MQTTClient(MQTT_BROKER_HOST)
    mqtt_client.connect()
except Exception as e:
    print("MQTT Client Failed to connect")


def delete_expired_session():
    try:
        query = "DELETE FROM clients WHERE expire_time < GETDATE()"
        cursor.execute(query)
        return 0
    except:
        return -1
    
def register_user(uid, perm_level):
    try:
        query = "INSERT INTO users VALUES (%s, %s)"
        uid = gen_id("users", "uid")
        cursor.execute(query, (uid, perm_level, ))
        return uid
    except:
        return -1
    
auth_code = ""
expiry = 0
    
def gen_auth_code():
    global auth_code, expiry
    code_list = []
    for i in range(6):
        code_list.append(str(random.randint(0, 9)))
    auth_code = "".join(code_list)
    expiry = time.time() + 60  # 1 minute from now
    return auth_code

def check_permission(uid, perms_list):
    try:
        query = "SELECT permission FROM users WHERE uid = %s"
        cursor.execute(query, (uid, ))
        ret = cursor.fetchone()
        permission = ret["permission"]
        return perms_list[permission]
    except:
        return -1

def auth_user(session_token):
    try:
        delete_expired_session()
        query = "SELECT * FROM clients WHERE token = %s AND expire_time > NOW()"
        cursor.execute(query, (session_token, ))
        session_dict = cursor.fetchone()
        if not session_dict:
            return -2
        return int(session_dict["uid"])
    except:
        return -1
    
def user_search(uid):
    try:
        query = "SELECT * FROM users WHERE uid = %s"
        cursor.execute(query, (uid, ))
        res = cursor.fetchall()
        if not res:
            return -2
        return 1
    except:
        return -1
    
def gen_session(uid, client_type):
    # Client Type 0 = Mobile 1 = Services 2 = Browser for root
    try:
        session_token = secrets.token_hex(32)
        query = "INSERT INTO clients VALUES (%s, %s, %s, %s, %s)"
        expire_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 3600))
        client_id = gen_id("clients", "id")
        
        cursor.execute(query, (client_id, uid, session_token, client_type, expire_time, ))

        return session_token
    except:
        return -1

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
    
def get_services_address():
    address = {}
    for key in services.keys():
        try:
            address[services[key]["service_id"]] = socket.gethostbyname(services[key]["service_domain"])
        except:
            address[key] = 0
    
    return address
    
@app.route("/root_auth", methods=['GET', 'POST'])

def root_auth():
    if request.method == 'GET':
        root_exist = user_search(0)
        if root_exist != 1:
            return "Root user does not Exist, register first!", 403
        return render_template("root_auth.html")
    elif request.method == 'POST':
        root_exist = user_search(0)
        if root_exist != 1:
            return "Root user does not Exist, register first!", 403
        try:
            req_root_password = request.form["password"]
        except:
            return "Request Error", 400
        try:
            # auth root user
            query = "SELECT * FROM rootuser"
            cursor.execute(query)
            res = cursor.fetchone()
            root_password = res["password"]
        except:
            return "Internel server error", 500
        try:
            if bcrypt.check_password_hash(root_password, req_root_password):
                session_token = gen_session(0, 2)  # Generate session for root user (uid=0)
                if session_token == -1:
                    return "Session generation failed", 500
                response = app.make_response("Authentication success")
                response.set_cookie('session_token', session_token) # session cookie for root user
                return response
            else:
                return "Password Invalid", 403
        except:
            return "There was Problem with a backend", 500
        
@app.route("/service_connect", methods=['GET'])

def service_connect():
    services_address = get_services_address()
    for key in services_address:
        if request.remote_addr == services_address[key]:
            return gen_session(10000 + int(key), 1)
        else:
            continue
    return f"No Services found for ip address {request.remote_addr}", 403

@app.route("/connect", methods=['GET', 'POST'])

def connect():
    if request.method == 'GET':
        if user_search(0) != 1:
            return "Root user does not Exist, register first!", 403
        session_token = request.cookies["session_token"]
        if auth_user(session_token) == 0:
            # Access Granted
            gen_auth_code()
            return render_template("login.html", auth_code=auth_code)
        else:
            return "Forbidden", 403

    elif request.method == 'POST':
        req_dict = request.get_json()
        req_uid = req_dict["uid"]
        req_auth_code = req_dict["auth_code"]
        if req_auth_code == auth_code:
            return gen_session(req_uid, 1)
        else:
            return "Invalid code", 403
        
@app.route("/renew_session", methods=['GET', 'POST'])

def renew_session():
    try:
        unintended_uid = [0]
        if "Session-Token" not in request.headers:
            return "Missing session token", 400
        uid = auth_user(request.headers["Session-Token"])
        if uid == -1:
            return "Server Error", 500
        elif uid == -2:
            return "Invalid Session", 403
        elif uid in unintended_uid:
            return "Unintended uid", 400
        new_session = gen_session(uid, 1)
        if new_session == -1:
            return "Failed to generate new session", 500
        return new_session
    except Exception as e:
        print(f"Error in renew_session: {str(e)}")
        return "Internal Server Error", 500
        
    
        
@app.route("/register", methods=['GET', 'POST'])

def register():
    root_search_res = user_search(0)
    # User generation
    if root_search_res != -2:
        auth_stat = auth_user(0) # Tries root user authentication
        if auth_stat == -2:
            return "Invalid Session", 403 # Session Invalid
        elif auth_stat == -1:
            return "Internal Server Error", 500 # Server Error
        # Registration Process
        if auth_stat == 0:
            if request.method == 'GET':
                return render_template("register.html")

            elif request.method == 'POST':
                try:
                    uid = gen_id("users", "uid")
                    if uid == -1:
                        return "UID generation Failed", 500
                    permission_input = request.form["permission"]
                    if permission_input == "Admin":
                        permission = 1
                    elif permission_input == "User":
                        permission = 2
                    else:
                        return "Invalid Request", 400
                    query = "INSERT INTO users VALUES (%s, %s)"
                    cursor.execute(query, (uid, permission, ))
                    return f"Process Successful, new uid is {uid}", 200
                except:
                    return "Internal Server Error", 500
    else:
        if request.method == 'GET':
            return render_template("root_register.html")
        elif request.method == 'POST':
            try:
                uid = gen_id("users", "uid")
                if uid != 0:
                    return "Error, root user already exists", 500
                permission = 0 # root user
                if request.form["password"] != request.form["confirm_password"]:
                    return "Check Password", 400
                password = request.form["password"]
                hash_pw = bcrypt.generate_password_hash(password)
                try:
                    query = "INSERT INTO users VALUES (%s, %s)"
                    cursor.execute(query, (uid, permission, ))
                    query = "INSERT INTO rootuser VALUES (%s, %s)"
                    cursor.execute(query, (0, hash_pw, ))
                except:
                    return "Database Error", 500
            except:
                return "Internal Server Error", 500
            return "Registration Sucessful", 200

@app.route("/users", methods=['GET'])

def users():
    # permission list
    get_permission = [2, 2, 2, 2]
    
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    # get users info
    try:
        # no permission validation because all session have access to this backend
        query = "SELECT uid FROM users WHERE uid <> 0"
        cursor.execute(query)
        ret = cursor.fetchall()
    except:
        return "Internal Server Error", 500
    return str(ret)

@app.route("/protocol/mqtt/getstats", methods=['GET'])

def getstats():
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat

    try:
        # 약간의 대기 필요 (MQTT 연결이 비동기이므로)
        time.sleep(1)
        stats = mqtt_module.get_stats_from_clients(mqtt_client)
        return {"stats": stats}
    except Exception as e:
        app.logger.error(f"Error in getstats: {str(e)}")
        return f"Error: {str(e)}", 500
        
@app.route("/protocol/mqtt/command", methods=['POST'])

def command():
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    
    req_dict = request.get_json()
    topic = req_dict["topic"]
    device_id = req_dict["device_id"]
    command = req_dict["command"]

    try:
        ret = mqtt_module.operate(mqtt_client, device_id, command, topic)
    except Exception as e:
        print(f"Error in getstats")
        return f"Internal Server Error", 500
    if type(ret) == str:
        return f"Error in process"

    if ret == 0:
        return "Operation Success", 200
    
    return "Internal Server Error", 500

@app.route("/location/logs", methods=['GET', 'POST', 'DELETE'])

def logs():
    # permission
    get_permission = [0, 1, 1, 2]
    post_permission = [0, 1, 1, 0]

    
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if(request.method == 'GET'):
        try:
            dict_req = request.get_json()
            uid = dict_req["uid"]
            # Permission Validation
            if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
                return "Permission Denied", 403
            search_time = dict_req["search_time"]
            query = "SELECT id, uid, ST_AsText(coordinate) as coordinate, time FROM locationlog WHERE uid = %s AND time >= %s"
            cursor.execute(query, (uid, search_time))
            ret = cursor.fetchall()
            if not ret:
                return "No data found for uid: {} after location_id: {}".format(uid, search_time), 404
        except:
            return "Internal Server Error", 500
        return str(ret)
        
    elif(request.method == 'POST'):
        try:
            # Gets uid from session_uid
            if check_permission(session_uid, post_permission) in [0]:
                return "Permission Denied", 403
            get_dict = request.get_json()
            coordinate = get_dict["coordinate"]
            issued = get_dict["time"]
            location_id = gen_id("locationlog", "id")
            if location_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO locationlog VALUES (%s, %s, ST_GeomFromText(%s), %s)"
            ret = cursor.execute(query, (location_id, session_uid, coordinate, issued))
        except:
            return f"POST unsuccessful, {ret}", 500
        return "Success"

@app.route("/location/latest", methods=['GET'])

def latest():
   # permission
    get_permission = [0, 1, 1, 2]
    
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat

    # Process
    
    get_dict = request.get_json()
    uid = get_dict["uid"]
    
    query = "SELECT id, uid, ST_AsText(coordinate) as coordinate, time FROM locationlog WHERE uid = %s ORDER BY time DESC LIMIT 1"
    cursor.execute(query, (uid, ))
    ret = cursor.fetchone()

    return str(ret)

@app.route("/location/fav/point", methods=['GET', 'POST', 'DELETE'])

def point():
    # permission
    get_permission = [0, 1, 1, 2]
    post_permission = [0, 0, 0, 2]
    delete_permission = [0, 1, 1, 2]

    
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if(request.method == 'GET'):
        dict_req = request.get_json()
        uid = dict_req["uid"]
        # Permission Validation
        if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
            return "Permission Denied", 403
        query = "SELECT id, uid, alias, ST_AsText(coordinate) as coordinate, status FROM userfavlocation WHERE uid = %s"
        cursor.execute(query, (uid, ))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for uid: {}".format(uid)
        return str(ret)
    
    # This middleware is usually used by services
    elif(request.method == 'POST'):
        try:
            get_dict = request.get_json()
            # Get uid by request
            uid = get_dict["uid"]
            if check_permission(session_uid, post_permission) in [0]:
                return "Permission Denied", 403
            coordinate = get_dict["coordinate"]
            alias = get_dict["alias"]
            status = get_dict["status"]
            point_id = gen_id("userfavlocation", "id")
            if point_id == -1:
                return "POST unsuccessful, Error while id generation"
            query = "INSERT INTO userfavlocation VALUES (%s, %s, %s, ST_GeomFromText(%s), %s)"
            ret = cursor.execute(query, (point_id, uid, alias, coordinate, status))
        except:
            return f"POST unsuccessful, {ret}", 500
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            point_id = get_dict["point_id"]
            uid = get_dict["uid"] # point_id owner uid must be validated before removing this from request
            if check_permission(session_uid, delete_permission) in [0, 1] and uid != session_uid:
                return "Permission Denied", 403
            query = "DELETE FROM userfavlocation WHERE id = %s AND uid = %s"
            ret = cursor.execute(query, (point_id, uid))
        except:
            return "DELETE unsuccessful", 500
        return "Success"
    
@app.route("/location/fav/route", methods=['GET', 'POST', 'DELETE'])

def route():
    # permission
    get_permission = [0, 1, 1, 2]
    post_permission = [0, 0, 0, 2]
    delete_permission = [0, 1, 1, 2]

    
    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if(request.method == 'GET'):
        # Load Request
        try:
            dict_req = request.get_json()
            startlocation_id = dict_req["startlocation_id"]
        except:
            return "Error while Loading Request", 500

        # get uid for auth
        try:
            query = "SELECT uid FROM userfavlocation WHERE id = %s"
            cursor.execute(query, (startlocation_id, ))
            ret = cursor.fetchone()
            uid = ret["uid"]
        except:
            return "Error while getting uid from location_id for auth", 500
        
        # Permission Validation
        if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
            return "Permission Denied", 403
        
        # query
        query = "SELECT id, startlocation_id, endlocation_id, ST_AsText(route) AS route, status FROM userfavroute WHERE startlocation_id = %s"
        cursor.execute(query, (startlocation_id, ))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for startlocation_id: {}".format(startlocation_id), 404
        return str(ret)
    
    elif(request.method == 'POST'):
        try:
            # Permission  Validation
            if check_permission(session_uid, post_permission) in [0]:
                return "Permission Denied", 403
            
            # Process Request
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
            return f"POST unsuccessful, {ret}", 500
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            route_id = get_dict["route_id"]
        except:
            return "Error while processing request", 500

        try:
            query = "SELECT startlocation_id FROM userfavroute WHERE id = %s"
            cursor.execute(query, (route_id, ))
            ret = cursor.fetchone()
            location_id = ret["startlocation_id"]
            query = "SELECT uid FROM userfavlocation WHERE id = %s"
            cursor.execute(query, (location_id, ))
            ret = cursor.fetchone()
            uid = ret["uid"]
        except:
            return "Error while getting uid from route_id for auth", 500
        
        if check_permission(session_uid, delete_permission) in [0, 1] and uid != session_uid:
                return "Permission Denied", 403
        try:
            query = "DELETE FROM userfavroute WHERE id = %s"
            ret = cursor.execute(query, (route_id, ))
            return "Success"
        except:
            return "DELETE unsuccessful", 500

@app.route("/event/visits", methods=['GET'])

def visits():
    get_permission = [0, 1, 1, 2]

    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    try:
        # Permission Validation
        if check_permission(session_uid, get_permission) in [0]:
            return "Permission Denied", 403
        visit_identifier = 0
        dict_req = request.get_json()
        location_id = dict_req["location_id"]
        lookup_days = dict_req["lookup_days"]
        query = 'SELECT count(*) AS visit_times FROM eventlog WHERE location_id = %s AND about = %s AND time BETWEEN NOW() - INTERVAL %s DAY AND NOW()'
        cursor.execute(query, (location_id, visit_identifier, lookup_days, ))
        ret = cursor.fetchone()
    except:
        return "Internal Server Error", 500
    return str(ret)

@app.route("/event/eventlogs", methods=['GET', 'POST', 'DELETE'])

def eventlogs():
    get_permission = [0, 1, 1, 2, 2]
    post_permission = [0, 1, 1, 2, 2]
    delete_permission = [0, 1, 1, 2, 2]

    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if(request.method == 'GET'):
        # Permission Validation
        if check_permission(session_uid, get_permission) in [0]:
            return "Permission Denied", 403
        dict_req = request.get_json()
        event_id = dict_req["location_id"]
        query = "SELECT * FROM eventlog WHERE location_id = %s"
        cursor.execute(query, (event_id, ))
        ret = cursor.fetchall()
        if not ret:
            return "No data found for event_id: {}".format(event_id), 404
        return str(ret)
    
    elif(request.method == 'POST'):
        # request process
        try:
            get_dict = request.get_json()
            issued = get_dict["time"]
            location_id = get_dict["location_id"]
            about = get_dict["about"]
            event_id = gen_id("eventlog", "id")
            if event_id == -1:
                return "POST unsuccessful, Error while id generation"
        except:
            return "Error while processing request", 500
        # get uid for auth
        try:
            query = "SELECT uid FROM userfavlocation WHERE id = %s"
            cursor.execute(query, (location_id, ))
            ret = cursor.fetchone()
            uid = ret["uid"]
        except:
            return "Error while getting uid from location_id for auth", 500
        
        # Permission Validation
        if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
            return "Permission Denied", 403
        
        try:
            query = "INSERT INTO eventlog VALUES (%s, %s, %s, %s)"
            ret = cursor.execute(query, (event_id, location_id, issued, about, ))
        except:
            return f"POST unsuccessful, {ret}", 404
        return "Success"
    
    elif(request.method == 'DELETE'):
        try:
            get_dict = request.get_json()
            event_id = get_dict["event_id"]
        except:
            return "Error while processing request", 500
        try:
            query = "SELECT location_id FROM eventlog WHERE id = %s"
            cursor.execute(query, (event_id, ))
            ret = cursor.fetchone()
            location_id = ret["location_id"]
            query = "SELECT uid FROM userfavlocation WHERE id = %s"
            cursor.execute(query, (location_id, ))
            ret = cursor.fetchone()
            uid = ret["uid"]
        except:
            return "Error while getting uid from event_id for auth", 500
        if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
            return "Permission Denied", 403
        try:
            query = "DELETE FROM eventlog WHERE id = %s"
            ret = cursor.execute(query, (event_id, ))
            return "Success"
        except:
            return "Error while interacting with database", 500

@app.route("/notification/getnoti", methods=['GET'])

def getnoti():
    get_permission = [0, 1, 1, 2]

    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    try:
        notification_id = request.headers["id"]
        notification_id = int(notification_id)
    except:
        return "Bad request", 400
    try:
        cursor.execute("SELECT * FROM usernotifications WHERE id = %s", (notification_id,))
        ret = cursor.fetchall()
        
        if not ret:
            return "No notification found for {}".format(notification_id), 404
    except:
        return f"Error: {ret}", 500
    return str(ret)
    
@app.route("/notification/postnoti", methods=['POST'])

def postnoti():
    post_permission = [0, 2, 0, 2]

    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if check_permission(session_uid, post_permission) in [0]:
            return "Permission Denied", 403
    dict_req = request.get_json()
    uid = dict_req["uid"] # changes
    content = dict_req["content"]
    issue = dict_req["time"]
    about = dict_req["about"]
    uid = int(uid)
    query = "INSERT INTO usernotifications VALUES (%s, %s, %s, %s, %s, %s)"
    notification_id = gen_id("usernotifications", "id")

    try:
        cursor.execute(query, (notification_id, uid, content, issue, 0, about))
    except:
        return "Error"
    conn.commit()
    return "Success"

@app.route("/notification/sync", methods=['GET', 'POST'])

def sync():
    get_permission = [0, 1, 1, 0]
    post_permission = [0, 2, 0, 2]

    # auth feature
    try:
        auth_stat = auth_user(request.headers["Session-Token"])
    except:
        return "Session not found", 403
    if auth_stat == -1:
        return "Authentication Server Error", 500
    elif auth_stat == -2:
        return "Invalid Session", 403
    session_uid = auth_stat
    if request.method == 'GET':
        try:
            cursor.execute("SELECT id FROM usernotifications WHERE uid = %s AND stat = %s", (session_uid, 0,))

            ret = cursor.fetchall()
            if not ret:
                return "No data to sync", 404
        except:
            return f"Error: {ret}", 500
        return str(ret)

    # POST
    elif request.method == 'POST':
        # Load Request
        try:
            req_dict = request.get_json()
            req_notification_id = req_dict["notification_id"]
        except:
            return "Required data not in request", 400
        
        # Permission Validation
        try:
            query = "SELECT uid FROM usernotifications WHERE id = %s"
            cursor.execute(query, (req_notification_id, ))
            ret = cursor.fetchone()
            uid = ret["uid"]
        except:
            return "Error while getting uid from notification_id for auth", 500
        
        if check_permission(session_uid, get_permission) in [0, 1] and uid != session_uid:
            return "Permission Denied", 403
        
        # Process
        try:
            query = "UPDATE usernotifications SET stat = %s WHERE id = %s"
            cursor.execute(query, (1, req_notification_id, ))
            return "OK", 200
        except:
            return "Internal Server Error", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)