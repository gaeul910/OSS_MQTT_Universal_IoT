from flask import Flask, render_template, request

app = Flask(__name__)

# Please Note that responses could change when DB is linked.

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

if __name__ == "__main__":
    app.run(debug=True)