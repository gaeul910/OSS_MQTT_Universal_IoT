from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/api/location/getdata")

def getdata():
    uid = request.args.get("uid", "str")
    if(uid == "sample-uid"):
        return render_template("location.json")
    return "Request by UID is still under development"

@app.route("/api/location/postdata", methods=['post'])

def postdata():
    uid = request.args("uid", "str")
    jsonoutput = open("templates/locationforupload.json", "w")
    jsonoutput.write(request.data)
    return

if __name__ == "__main__":
    app.run(debug=True)