import flask
import sqlite3
import secrets
from flask import Flask, request, make_response, render_template
from util.DB_Interface import DB
import json

app = Flask(__name__)
db = DB()


# Helpers
def gen_token():
    token = secrets.token_hex(32)
    while db.exists("USER").where(curr_token=token):
        token = secrets.token_hex(32)
    return token

def unpack(j,*args,**kargs):
    r = [j.get(arg,None) for arg in args]
    if kargs.get("required",False):
        [abort(kargs.get("error",400)) for e in r if e == None]
    return r

# endpoints
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/login",methods=["POST"])
@endpoint("json_post",auth=False)
def login(j):
    if not db.exists("USER").where(username=un,password=ps):
        abort(405)
    t = gen_token()
    db_r = db.update("USER").set(curr_token=t).where(username=un)
    db_r.execute()
    resp = make_response(json.dumps({
        "msg": "login successful"
    }))
    resp.set_cookie('session',t)
    return resp

@app.route("/api/user",methods=["GET"])
def user():
    (t,) = unpack(request.cookies,"session",required=True,error=405)
    u = db.select("USER").where(curr_token=t).execute()
    resp = make_response(json.dumps({
        "name": u[0]
    }))
    return resp

if __name__ == "__main__":
    app.run(debug=True)
