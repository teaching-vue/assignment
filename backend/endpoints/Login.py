import falcon
import json
import secrets
from util.DB_Interface import DB

class Login:
    def __init__(self, db_conn):
        self.db = DB(db_conn)
    def on_get(self, req, resp):
        resp.status = falcon.HTTP_405
    def gen_token(self):
        token = secrets.token_hex(32)
        while self.db.exists("USER").where(curr_token=token):
            token = secrets.token_hex(32)
        return token
    def on_post(self, req, resp):
        j = json.load(req.stream) if req.content_length else {};
        un = j.get("username",None)
        ps = j.get("password",None)
        if not un or not ps:
            resp.status = falcon.HTTP_400
            return
        valid = self.db.exists("USER").where(username=un,password=ps)
        if not valid:
            resp.status = falcon.HTTP_405
            return
        token = self.gen_token()
        db_request = self.db.update("USER").set(curr_token=token).where(username=un)
        db_request.execute() # you need to explicity push the changes
        resp.set_cookie("session",token)
        resp.status = falcon.HTTP_200
