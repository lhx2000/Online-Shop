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

number_set = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']


def myhash(pwd,un,salt):
    H = hashlib.md5()
    H.update((pwd+un+salt).encode("utf-8"))
    return H.hexdigest()

User = Blueprint('User',__name__)

@User.route('/SignIn')
def signin_page():
    return render_template("SignIn.html")
     
@User.route('/SignIn' , methods = ['POST'])
def signin():
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
    print(keys)
    if(keys == None):
        message = "用户名或密码错误！"
        validate = 0
    if validate:
        keyID = keys[0][1:]
        key = keys[1]
        keyHash = myhash(passwd,username,keyID)
        if keyHash != key:
            message = "用户名或密码错误！"
            validate = 0
    if validate:
        session['user_info'] = keys[0]
        conn.commit()
        conn.close()
        return redirect("/HomePage")
    else:
        flash(message)
        return render_template("SignIn.html")
        
    
@User.route('/SignUp')
def signup_page():
    return render_template("SignUp.html")

@User.route('/SignUp' , methods = ['POST'])
def signup():
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()

    telnumber = request.form["telnumber"]
    username = request.form["username"]
    passwd = request.form["passwd"]
    passwd2 = request.form["passwd2"]
    validate = 1

    if len(telnumber)==0 or len(telnumber)>20:
        message = "请输入正确的电话号码！"
        validate = 0
    for i in telnumber:
        if i not in number_set:
            message = "请输入正确的电话号码！"
            validate = 0
            break
    if len(username) == 0 or len(passwd) == 0:
        message = "用户名或密码不能为空！"
        validate = 0
    if len(username) > 10 or len(passwd) > 10:
        message = "用户名或密码不能超过10个字符！"
        validate = 0
    if passwd != passwd2:
        message = "两次密码不一致！"
        validate = 0
    for i in username + passwd:
        if i not in key_set:
            message = "用户名或密码只允许使用字母和数字！"
            validate = 0
            break
    mycursor.execute("SELECT count(*) FROM USER WHERE Uname = '" + username + "'")
    if(mycursor.fetchone()[0] != 0):
        message = "用户名已存在！"
        validate = 0
    if validate:
        mycursor.execute("SELECT MAX(Urow) FROM USER")
        count = mycursor.fetchone()[0] + 1
        ID = 'U' + str(202000000 + count)
        passwdHash = myhash(passwd,username,ID[1:])
        mycursor.execute("INSERT INTO USER (UID,Uname,Upassword,Utelnumber,Urow) VALUES ('%s','%s','%s','%s','%s')" % (ID,username,passwdHash,telnumber,count))
        message = "注册成功！"
    flash(message)
    conn.commit()
    conn.close()
    return render_template("SignUp.html")

@User.route("/Account")
def showAccount():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    if request.args.get("UID") != None:
        UID = request.args['UID']
    else:
        return redirect('/Account?UID=' + session.get("user_info"))
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT UID,Uname,Umail,Utelnumber,Uage,Usex,Uamount FROM USER WHERE UID = '" + UID + "'")
    info = mycursor.fetchone()
    mycursor.execute("SELECT Gname,Gsale,Sdate,GID FROM STORE,GAME WHERE Suser = '" + UID + "' AND STORE.Sgame = GAME.GID")
    sto = mycursor.fetchall()
    conn.commit()
    conn.close()
    return render_template("Account.html" , info = info , sto = sto)

@User.route("/Account" , methods = ["POST"])
def Account():
    if session.get('user_info') == None:
        return redirect('/SignIn')
    if len(request.form) == 4:
        UID = request.args['UID']
        Umail = request.form['Umail']
        Utelnumber = request.form['Utelnumber']
        Uage = request.form['Uage']
        Usex = request.form['Usex']
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("UPDATE USER SET Umail = '%s',Utelnumber = '%s',Uage = '%s',Usex = '%s' WHERE UID = '%s'" % (Umail,Utelnumber,Uage,Usex,UID))
        mycursor.execute("SELECT UID,Uname,Umail,Utelnumber,Uage,Usex,Uamount FROM USER WHERE UID = '" + UID + "'")
        info = mycursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("Account.html" , info = info)
    elif len(request.form) == 3:
        oldPasswd = request.form["oldPasswd"]
        newPasswd = request.form["newPasswd"]
        newPasswd2 = request.form["newPasswd2"]
        UID = request.args["UID"]
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT Uname,Upassword FROM USER WHERE UID = '" + UID + "'")
        result = mycursor.fetchone()
        Unm = result[0]
        Upasswd = result[1]
        print(Unm,Upasswd)
        if myhash(oldPasswd,Unm,UID[1:]) != Upasswd:
            return "<h3>原密码输入不正确！</h3>"
        if newPasswd != newPasswd2:
            return "<h3>两次新密码输入不一致！</h3>"
        for i in newPasswd:
            if i not in key_set:
                return "<h3>密码只允许使用字母和数字！</h3>"
        UnewPasswd = myhash(newPasswd,Unm,UID[1:])
        mycursor.execute("UPDATE USER SET Upassword = '%s' WHERE UID = '%s'" % (UnewPasswd,UID))
        mycursor.execute("SELECT UID,Uname,Umail,Utelnumber,Uage,Usex,Uamount FROM USER WHERE UID = '" + UID + "'")
        info = mycursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("Account.html" , info = info)
    elif len(request.form) == 1:
        Uamount = request.form["ammount"]
        UID = request.args["UID"]
        conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
        mycursor = conn.cursor()
        mycursor.execute("SELECT Uamount FROM USER WHERE UID = '" + UID + "'")
        oldAmount = mycursor.fetchone()[0]
        mycursor.execute("UPDATE USER SET Uamount =  '%f' WHERE UID = '%s'" % (oldAmount+float(Uamount),UID))
        mycursor.execute("SELECT UID,Uname,Umail,Utelnumber,Uage,Usex,Uamount FROM USER WHERE UID = '" + UID + "'")
        info = mycursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("Account.html" , info = info)

@User.route('/quit')
def quit():
    session['user_info'] = None
    return redirect('/SignIn') 

@User.route('/Comment' , methods = ['POST'])
def Comment():
    print(request.form)
    star = request.form.get('star')
    com = request.form.get('com')
    game = request.form.get('game')
    conn = sqlite3.connect("app\\database\\Stream.db",check_same_thread = False)
    mycursor = conn.cursor()
    mycursor.execute("SELECT MAX(Crow) FROM COMMENT")
    count = mycursor.fetchone()[0] + 1
    Ccount = 'C' + str(202000000 + count)
    mycursor.execute("INSERT INTO COMMENT (CID,Cuser,Cgame,Cstar,Crow,Ccontent) VALUES ('%s','%s','%s','%d','%d','%s')" % (Ccount,session.get('user_info'),game,int(star),count,com))
    conn.commit()
    conn.close()
    return redirect('/Game?GID=' + game)




    