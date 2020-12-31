from flask import Blueprint
from flask import render_template
from flask import request
from flask import flash
from flask import session
from flask import redirect
import sqlite3
import hashlib

key_set = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
           'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
           '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']

def myhash(pwd,un,salt):
    H = hashlib.md5()
    H.update((pwd+un+salt).encode("utf-8"))
    return H.hexdigest()

Admin = Blueprint('Admin',__name__)

@Admin.route('/AdminLogin')
def showAdminPage():
    return render_template('AdminLogin.html')

@Admin.route('/AdminLogin' , methods = ['POST'])
def adminLogin():
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()

    username = request.form["username"]
    passwd = request.form["passwd"]
    validate = 1
    if len(username) == 0 or len(passwd) == 0:
        message = "用户名或密码不能为空！"
        validate = 0
    if len(username) > 10 or len(passwd) > 10:
        message = "请输入正确格式的用户名或密码！"
        validate = 0
    for i in username + passwd:
        if i not in key_set:
            message = "请输入正确格式的用户名或密码！"
            validate = 0
            break
    mycursor.execute("SELECT UID,Upassword FROM USER WHERE Uname = '" + username + "'")
    keys = mycursor.fetchone()
    if(keys == None):
        message = "用户名或密码错误！"
        validate = 0
    if validate:
        keyID = keys[0]
        if keyID[0] != 'A':
            message = "您没有管理员权限！"
            validate = 0
        key = keys[1]
        keyHash = myhash(passwd,username,keyID[1:])
        if keyHash != key:
            message = "用户名或密码错误！"
            validate = 0
    if validate:
        session['user_info'] = keys[0]
        conn.commit()
        conn.close()
        return render_template("AdminPage.html")
    else:
        flash(message)
        return render_template("AdminLogin.html")


@Admin.route('/UserManager')
def showUserManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT UID,Uname,Umail,Uamount FROM USER ORDER BY UID")
    u = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('UserManager.html', u = u)

@Admin.route('/UserManager' , methods = ['POST'])
def userManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    if request.form.get('quit') == "退出":
        session['user_info'] = None
        return redirect('/AdminLogin')
    if request.form.get('search') == None or request.form.get('search') == 'IWannaAll!':    
        num = ""
        oper = ""
        for i,j in request.form.items():
            num = i
            oper = j
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        if oper == "提升":
            newNum = 'A' + num[1:]
            mycursor.execute("UPDATE USER SET UID = '%s' WHERE UID = '%s'" % (newNum,num))
        elif oper == "删除":
            mycursor.execute("DELETE FROM USER WHERE UID = '" + num + "'")
        mycursor.execute("SELECT UID,Uname,Umail,Uamount FROM USER ORDER BY UID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('UserManager.html' , u = u)
    else:
        keyword = request.form.get('search')
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT UID,Uname,Umail,Uamount FROM USER WHERE Uname LIKE '%" + keyword + "%' ORDER BY UID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('UserManager.html' , u = u)

@Admin.route('/GameManager')
def showGameManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME ORDER BY GID")
    u = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('GameManager.html', u = u)

@Admin.route('/GameManager', methods = ["POST"])
def GameManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    if request.form.get('quit') == "退出":
        session['user_info'] = None
        return redirect('/AdminLogin')
    if len(request.form) == 7:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT MAX(Grow) FROM GAME")
        count =  mycursor.fetchone()[0] + 1
        GID = 'G' + str(202000000 + count)
        mycursor.execute("INSERT INTO GAME (GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore,Grow,Ginfo) VALUES ('%s','%s','%s','%s','%s','%s','%s','%d','%s')" % (GID,request.form["Gname"],request.form["Gfirm"],request.form["Gtype"],request.form["Gdate"],request.form["Gsale"],request.form["Gscore"],count,request.form['Ginfo']))
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('GameManager.html', u = u)
    elif len(request.form) == 2:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        content = request.form['search']
        w = request.form["searchRange"]
        mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME WHERE " + w + " LIKE '%" + content + "%' ORDER BY GID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('GameManager.html', u = u)
    elif len(request.form) == 1:
        num = ""
        oper = ""
        for i,j in request.form.items():
            num = i
            oper = j
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        if oper == "修改":
            mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME WHERE GID = '" + num + "'")
            u = mycursor.fetchone()
            return render_template("ChangeGameInfo.html" , u = u)
        elif oper == "删除":
            mycursor.execute("DELETE FROM GAME WHERE GID = '" + num + "'")
            mycursor.execute("SELECT GID,Gname,Gfirm,Gtype,Gdate,Gsale,Gscore FROM GAME ORDER BY GID")
            u = mycursor.fetchall()
            conn.commit()
            conn.close()
            return render_template('GameManager.html' , u = u)

@Admin.route('/ChangeGameInfo' , methods = ["POST"])
def ChangeGameInfo():
    newScore = request.form['Gscore']
    newSale = request.form['Gsale']
    num = ''
    for i in request.form.keys():
        num = i
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("UPDATE GAME SET Gsale = '%s',Gscore = '%s' WHERE GID = '%s'" % (newSale,newScore,num))
    conn.commit()
    conn.close()
    return redirect("/GameManager")
    

@Admin.route('/OrderManager')
def showOrderManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT OID,Ouser,Ogame,Osale,Odate,Opayornot FROM ORDERS ORDER BY OID")
    u = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('OrderManager.html', u = u)

@Admin.route('/OrderManager' , methods = ["POST"])
def OrderManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    if request.form.get('quit') == "退出":
        session['user_info'] = None
        return redirect('/AdminLogin')
    if len(request.form) == 2:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        content = request.form['search']
        w = request.form["searchRange"]
        mycursor.execute("SELECT OID,Ouser,Ogame,Osale,Odate,Opayornot FROM ORDERS WHERE " + w + " LIKE '%" + content + "%' ORDER BY OID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('OrderManager.html', u = u)
    elif len(request.form) == 1:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        num = ""
        for i in request.form.keys():
            num = i
        mycursor.execute("DELETE FROM ORDERS WHERE OID = '" + num + "'")
        mycursor.execute("SELECT OID,Ouser,Ogame,Osale,Odate,Opayornot FROM ORDERS ORDER BY OID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('OrderManager.html', u = u)
    
@Admin.route('/CommentManager')
def showCommentManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT CID,Cuser,Cgame,Cstar,Ccontent FROM COMMENT ORDER BY CID")
    u = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template('CommentManager.html', u = u)

@Admin.route('/CommentManager' , methods = ["POST"])
def CommentManager():
    if session.get('user_info') == None or session.get('user_info')[0] != 'A':
        return redirect('/AdminLogin')
    if request.form.get('quit') == "退出":
        session['user_info'] = None
        return redirect('/AdminLogin')
    if len(request.form) == 2:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        content = request.form['search']
        w = request.form["searchRange"]
        mycursor.execute("SELECT CID,Cuser,Cgame,Cstar,Ccontent FROM COMMENT WHERE " + w + " LIKE '%" + content + "%' ORDER BY CID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('CommentManager.html', u = u)
    elif len(request.form) == 1:
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        num = ""
        for i in request.form.keys():
            num = i
        mycursor.execute("DELETE FROM COMMENT WHERE CID = '" + num + "'")
        mycursor.execute("SELECT CID,Cuser,Cgame,Cstar,Ccontent FROM COMMENT ORDER BY CID")
        u = mycursor.fetchall()
        conn.commit()
        conn.close()
        return render_template('CommentManager.html', u = u)
