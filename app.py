from flask import Flask, request, render_template, session, redirect, jsonify
import pandas as pd
from sqlalchemy import create_engine

app = Flask(__name__)

@app.route("/signup", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        user = request.form["user"]
        password = request.form["password"]
        inp = pd.DataFrame({"user":[user],"password":[password]})
        
        con = create_engine("sqlite:///users.sqlite")
        if "users" in con.table_names():
            users = pd.read_sql("users",con)
            if inp["user"].values[0] in users["user"]:
                return("Username already exists")
            inp.to_sql("users",con,index=False,if_exists = "append")
        else:
            inp.to_sql("users",con,index=False)
        
        users = pd.read_sql("users",con)
        
        return("input:" + inp.to_html() + "database:" + users.to_html())
    return render_template("signup.html")

@app.route("/", methods=["GET","POST"])
def home():
    if request.method=="POST":
        user = request.form["user"]
        password = request.form["password"]
        con = create_engine("sqlite:///users.sqlite")
        # inp = pd.DataFrame({"user":[user],"password":[password]}) 
        
        if "users" in con.table_names():
            users = pd.read_sql("users",con)
            print(users["user"])
            if user in users["user"].values:
                if password == users[users["user"]==user]["password"].values[0]:
                    session['logged_in'] = True
                    return("You are logged in")
                else:
                    return("Wrong Password" + users.to_html())
            else:
                return("User does not exist" + users.to_html())
        else:
            return("User database does not exist.")
            
    return render_template("login.html")

@app.route("/logout")
def logout():
    session['logged_in'] = False
    return("You are logged OUT")
    

@app.route("/getset", methods=["GET", "POST"])
def us():
    if session['logged_in'] != True:
        return("please log in")
    if request.method == "POST":
        inp = pd.DataFrame()
        keys = request.form["keys"].split(",")
        values = request.form["values"].split(",")
        inp["key"] = keys
        inp["value"] = values
        
        con = create_engine("sqlite:///db.sqlite")
        if "db" in con.table_names():
            db = pd.read_sql("db",con)
            db = pd.concat([db,inp])
            db.drop_duplicates("key",keep="last",inplace=True)
            db.sort_values("key",inplace=True)
            db.to_sql("db", con, index=False, if_exists="replace")
        else:
            db = inp.sort_values("key")
            db.to_sql("db", con, index=False, if_exists="replace")
        
        return(
            "input:" + inp.to_html()+
            "updated database: " + db.to_html())
    return render_template("form.html")



if __name__ == "__main__":
    app.secret_key='dq27'
    app.run(debug=True)