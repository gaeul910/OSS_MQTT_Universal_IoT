from flask import Flask, render_template, request

app = Flask(__name__)

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


if __name__ == "__main__":
    app.run(debug=True)