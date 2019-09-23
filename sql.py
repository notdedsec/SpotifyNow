import sqlite3
def execute(query):
    connection = sqlite3.connect("spotifynow.db")
    cursor = connection.cursor()
    cursor.execute(query)
    r = cursor.fetchall()
    connection.commit()
    connection.close()
    return(r)

ADD_USER = """INSERT OR IGNORE INTO userdb (userid, username, authtoken)
VALUES ("{}", "{}", "none");"""

ADD_TOKEN = """UPDATE userdb
SET authtoken = "{}"
WHERE userid = "{}";"""

DEL_USER = """DELETE
FROM userdb
WHERE userid = "{}";"""

LIST_USERS = """SELECT userid
FROM userdb;"""

GET_USER = """SELECT *
FROM userdb
WHERE userid = "{}";"""

CREATE_TABLE = """CREATE TABLE IF NOT EXISTS userdb (
    userid NVARCHAR(15) PRIMARY KEY,
    username NVARCHAR(30),
    authtoken NVARCHAR(300)
);"""

def add_user(userid, username):
    return(execute(ADD_USER.format(userid, username)))

def add_token(authtoken, userid):
    return(execute(ADD_TOKEN.format(authtoken, userid)))

def del_user(userid):
    return(execute(DEL_USER.format(userid)))

def list_users():
    return(execute(LIST_USERS))

def get_user(userid):
    return(execute(GET_USER.format(userid)))

def create_table():
    return(execute(CREATE_TABLE))
