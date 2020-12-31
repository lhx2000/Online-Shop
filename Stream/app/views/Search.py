from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import session
from flask import redirect
import datetime
import sqlite3

Search = Blueprint('Search',__name__)


@Search.route('/HomePage')
def showHomePage():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    if request.args.get('search') == "搜索":
        Range = request.args.get('range')
        content = request.args.get('content')
        url = "/SearchList?" + Range + "=" + content
        return redirect(url)
    return render_template("HomePage.html" , User = User)

@Search.route('/HomePage' , methods = ["POST"])
def HomePage():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    return render_template("HomePage.html" , User = User)

@Search.route('/SearchList')
def showSearchList():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    if len(request.args) == 0:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('SearchList.html' , u = u , User = User)
    if request.args.get('Gtype') != None:
        Gtype = request.args["Gtype"]
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME WHERE Gtype = '" + Gtype + "' ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('SearchList.html' , u = u , User = User)
    elif request.args.get('Gname') != None:
        Gname = request.args["Gname"]
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME WHERE Gname LIKE '%" + Gname + "%' ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('SearchList.html' , u = u , User = User)
    elif request.args.get('Gfirm') != None:
        Gfirm = request.args["Gfirm"]
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME WHERE Gfirm LIKE '%" + Gfirm + "%' ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('SearchList.html' , u = u , User = User)


@Search.route('/SearchList' , methods = ['POST'])
def SearchList():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    num = ""
    for i in request.form.keys():
        num = i
    return redirect('/Game?GID=' + num)

@Search.route('/Game')
def showGame():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    GID = request.args.get("GID")
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Ginfo,Gdate,Gsale,Gscore FROM GAME WHERE GID = '" + GID + "'")
    u = mycursor.fetchone()
    mycursor.execute("SELECT Uname,Cstar,Ccontent FROM USER,COMMENT WHERE COMMENT.CGAME = '" + GID + "' AND USER.UID = COMMENT.Cuser")
    v = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('Game.html' , u = u , v = v , User = User)

@Search.route('/Buy' , methods = ['POST'])
def Buy():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    num = ""
    oper = ""
    for i,j in request.form.items():
        num = i
        oper = j
    if oper == "我要买！！！":
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gsale FROM GAME WHERE GID = '" + num + "'")
        u = mycursor.fetchone()
        mycursor.execute("SELECT Uname,Uamount FROM USER WHERE UID = '" + session.get('user_info') + "'")
        v = mycursor.fetchone()
        mycursor.execute("SELECT COUNT(*) FROM STORE WHERE Suser = '%s' AND Sgame = '%s'" % (session.get('user_info'),u[0]))
        if(mycursor.fetchone()[0] != 0):
            return "<h1>您已拥有该游戏！</h1>"
        conn.commit()
        conn.close()
        return render_template("Buy.html" , u = u , v = v , User = User)
    else:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gsale FROM GAME WHERE GID = '" + num + "'")
        u = mycursor.fetchone()
        mycursor.execute("SELECT Uname,Uamount FROM USER WHERE UID = '" + session.get('user_info') + "'")
        v = mycursor.fetchone()
        time = datetime.datetime.now()
        time = time.strftime("%Y-%m-%d %H:%M:%S")
        mycursor.execute("INSERT INTO STORE (Suser,Sgame,Sdate) VALUES ('%s','%s','%s')" % (session.get('user_info'),u[0],time))
        mycursor.execute("UPDATE USER SET Uamount = '%f' WHERE UID = '%s'" % (v[1]-u[2],session.get('user_info')))
        conn.commit()
        conn.close()
        return redirect("/Account")

@Search.route('/Cancel' , methods = ["POST"])
def Cancel():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    User = session.get('user_info')
    print(request.form)
    num = ""
    oper = ""
    for i,j in request.form.items():
        num = i
        oper = j
    if oper == "删除":
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("DELETE FROM STORE WHERE Sgame = '" + num + "' AND Suser = '" + User + "'" )
        conn.commit()
        conn.close()
        return redirect('/Account')
    elif oper == "退货":
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT GID,Gname,Gsale FROM GAME WHERE GID = '" + num + "'")
        u = mycursor.fetchone()
        mycursor.execute("SELECT Uname,Uamount FROM USER WHERE UID = '" + session.get('user_info') + "'")
        v = mycursor.fetchone()
        mycursor.execute("SELECT Sdate FROM STORE WHERE Sgame = '" + num + "' AND Suser = '" + User + "'")
        buytime = mycursor.fetchone()[0]
        buytime = datetime.datetime.strptime(buytime,"%Y-%m-%d %H:%M:%S")
        nowtime = datetime.datetime.now()
        conn.commit()
        conn.close()
        if buytime + datetime.timedelta(days=1) < nowtime:
            return render_template("Cancel.html" , u = u , v = v , time = buytime , judge = 0)
        else:
            return render_template("Cancel.html" , u = u , v = v , judge = 1)
    else:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT COUNT(*) FROM STORE WHERE Sgame = '" + num + "' AND Suser = '" + User + "'")
        if mycursor.fetchone()[0] == 0:
            return redirect('/Account')
        mycursor.execute("SELECT Gsale FROM GAME WHERE GID = '" + num + "'")
        sale = mycursor.fetchone()[0]
        mycursor.execute("SELECT Uamount FROM USER WHERE UID = '" + session.get('user_info') + "'")
        amount = mycursor.fetchone()[0]
        mycursor.execute("DELETE FROM STORE WHERE Sgame = '" + num + "' AND Suser = '" + User + "'" )
        mycursor.execute("UPDATE USER SET Uamount = '%f' WHERE UID = '%s'" % (sale+amount,session.get('user_info')))
        conn.commit()
        conn.close()
        return redirect('/Account')





