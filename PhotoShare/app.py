######################################
# author ben lawson <balawson@bu.edu> 
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################

import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
import datetime
import random
import operator


# for image uploading
# from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'lilin1017'
app.config['MYSQL_DATABASE_DB'] = 'photoshare'
app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM Users")
users = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM Users")
    return cursor.fetchall()


class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    users = getUserList()
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    users = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(users):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user


'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'GET':
        return '''
			   <form action='login' method='POST'>
				<input type='text' name='email' id='email' placeholder='email'></input>
				<input type='password' name='password' id='password' placeholder='password'></input>
				<input type='submit' name='submit'></input>
			   </form></br>
		   <a href='/'>Home</a>
			   '''
    # The request method is POST (page is recieving data)
    email = flask.request.form['email']
    cursor = conn.cursor()
    # check if email is registered
    if cursor.execute("SELECT password FROM Users WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file

    # information did not match
    return "<a href='/login'>Try again</a>\
			</br><a href='/register'>or make an account</a>"


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('unauth.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register/", methods=['GET'])
def register():
    return render_template('register.html', supress='True', message = 'register for new account')


@app.route("/register/", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        date_of_birth = request.form.get('date_of_birth')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')

        print(email,password,firstname,lastname,date_of_birth,hometown,gender)


    except:
        print("Please re-register. Account in use")  # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO Users (email, password,firstname,lastname,date_of_birth,hometown,gender) VALUES ('{0}', '{1}','{2}','{3}','{4}','{5}','{6}')".format(email, password,firstname,lastname,date_of_birth,hometown,gender)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        user.name = (firstname+" "+lastname)
        flask_login.login_user(user)
        return render_template('profile.html', name=flask_login.current_user.name, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))



def getUsersPictures(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT imgdata, picture_id, caption FROM Pictures WHERE user_id = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id  FROM Users WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]


def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM Users WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True

def isAlbumUnique(album_id):
    # use this to check if an album_id has already been used
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Albums WHERE album_id = '{0}'".format(album_id)):
        # this means there are greater than zero entries with that album_id
        return False
    else:
        return True
# end login code

def isPictureUnique(picture_id):
    cursor = conn.cursor()
    if cursor.execute("SELECT *  FROM Pictures WHERE picture_id = '{0}'".format(picture_id)): 
        #this means there are greater than zero entries with that email
        return False
    else:
        return True

def getFriendList(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id2 FROM friends where user_id = '{0}'".format(user_id))
    return cursor.fetchall()

def getrecommondFriendList(user_id):
    cursor = conn.cursor()
    print(user_id)
    #cursor.execute('SELECT word FROM Associate GROUP BY word ORDER BY COUNT(*) DESC')
    #cursor.execute("SELECT F2.user_id2 FROM Friends AS F1 AND Friends AS F2 where  AND F2.user_id2 != F1.user_id AND F2.user_id IN (SELECT F1.user_id2 AS myF FROM FRIENDS AS F1 WHERE F1.user_id = '{0}'".format(user_id)))
    cursor.execute("SELECT user_id2 FROM friends where user_id = '{0}'".format(user_id))
    myfriend = cursor.fetchall()
    myfriend = [int(str(i).strip("()").split(",")[0]) for i in myfriend]
    allrec = []
    print(myfriend)
    for j in myfriend:
        cursor.execute("SELECT user_id FROM friends where user_id2 = '{0}'".format(j))
        f = cursor.fetchall()
        print(f)
        flst = []
        for i in f:
            flst += [int(str(i).strip("()").split(",")[0])]
        #flst = [k for k in flst if k != user_id and k not in myfriend]
        print(flst)
        flst = [k for k in flst if k != user_id and k not in myfriend]
        print('final flst',flst)
        allrec += flst
    print(allrec)
    return allrec

def getUsersAlbums(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums WHERE user_id = '{0}'".format(user_id))
    return cursor.fetchall()

def getAlbumId(album_name):
    cursor = conn.cursor()
    cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(album_name))
    return cursor.fetchall()

def getUserName(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT firstname, lastname FROM Users where user_id = '{0}'".format(user_id))
    return [[col.encode('utf8') if isinstance(col, unicode) else col for col in row] for row in cursor.fetchall()]


def getUsersPictures(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT p.imgdata, a.album_name, p.caption, p.picture_id from Pictures p, Albums a \
            WHERE a.user_id = '{0}' AND p.album_id = a.album_id".format(user_id))
    return cursor.fetchall()

def getAlbumsPhotos(album_name, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT p.imgdata, a.album_name, p.caption, p.picture_id from Pictures p, Albums a \
            WHERE a.user_id = '{0}' AND a.album_name = '{1}' AND p.album_id = a.album_id".format(user_id, album_name))
    return cursor.fetchall()

def photolike(picture_id, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Likes WHERE picture_id='{0}' AND user_id='{1}'".format(picture_id, user_id))
    return cursor.fetchall()


def isPictureBelongtoUser(picture_id, user_id):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Pictures WHERE picture_id='{0}' AND user_id='{1}'".format(picture_id, user_id)):
        return True
    else:
        return False

def check_like(picture_id,user_id):
    cursor = conn.cursor()
    if cursor.execute("SELECT * FROM Likes WHERE picture_id = '{0}' AND user_id = '{1}'".format(picture_id,user_id)):
        return True
    else:
        return False



@app.route('/profile')
@flask_login.login_required
def protected():
    return render_template('profile.html', name=flask_login.current_user.id, message="Here's your profile")


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/CreateAlbum/', methods=['GET', 'POST'])
@flask_login.login_required
def viewAlbums():
    if request.method == 'GET':
        user_id=getUserIdFromEmail(flask_login.current_user.id)
        album_id=getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
        if not album_id:
            return render_template("CreateAlbum.html", message='You have no albums')
        else:
            return render_template("CreateAlbum.html", message='You have these albums', viewAlbums=album_id)
    else:
        user_id=getUserIdFromEmail(flask_login.current_user.id)
        album_id = request.form.get('album_id')
        album_name = request.form.get('album_name')
        date_of_creation = request.form.get('date_of_creation')
        if isAlbumUnique(album_id):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Albums (album_id, album_name, date_of_creation, user_id) VALUES ('{0}', '{1}', '{2}', '{3}')".format(album_id, album_name, date_of_creation, user_id))
            conn.commit()
            album_id=getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
            return render_template("CreateAlbum.html", message='You have these albums', viewAlbums=album_id)
        else:
            return render_template("CreateAlbum.html", message='Album id: '+ str(album_id)+ ' has been taken')

###Ends Create Album###

@app.route('/upload/', methods=['GET'])
def upload_photo():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    return render_template('upload.html', uploadPhoto="lets upload photo", viewAlbums=getUsersAlbums(uid))

@app.route('/upload/', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        imgfile = request.files['photo']
        photo_data = base64.standard_b64encode(imgfile.read())
        caption = request.form.get('caption')
        album_id = request.form.get('album_id')
        #print "user_id: ", uid, ",binary data: ", imgfile, ",caption: ", caption, ",album_id:", album_id, "tag: ", tag

        cursor = conn.cursor()
        cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(album_id))
        album_id = int(str(album_id).strip("()").split(",")[0])

        print("start to upload photos")
        cursor.execute(
            "INSERT INTO Pictures(imgdata, caption, album_id,user_id) VALUES ('{0}', '{1}', '{2}','{3}')".format(photo_data, caption,
                                                                                               album_id,user_id))
        conn.commit()

        cursor.execute("SELECT picture_id FROM Pictures WHERE imgdata = '{0}' AND caption='{1}'".format(photo_data, caption))
        picture_id = int(cursor.fetchall()[0][0])
        # if len(tag) != 0:
        #     tag = tag.split(",")
        #     for x in tag:
        #         cursor.execute("INSERT INTO Tags (word, picture_id,user_id) VALUES ('{0}','{1}','{2}')".format(x,picture_id,user_id))
        #         conn.commit()
        tag = str(request.form.get('tag'))
        temp = []
        temp = tag.split(',')
        for i in range(len(temp)):
            cursor = conn.cursor()
            cursor.execute("SELECT word FROM Tags")
            AllTags=cursor.fetchall()
            tags = []
            for j in range(len(AllTags)):
                tags.append(AllTags[j][0])
            if temp[i] not in tags:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Tags (word) VALUES ('{0}')".format(temp[i]))
                cursor.execute("INSERT INTO Associate (word, picture_id) VALUES ('{0}', '{1}')".format(temp[i], picture_id,))
                conn.commit()
            else:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO Associate (word, picture_id) VALUES ('{0}', '{1}')".format(temp[i],picture_id))
                conn.commit()
        print('success')

        return render_template('profile.html', name= flask_login.current_user.id, message='Photo uploaded!', photos=getUsersPictures(user_id))
    else:
        return flask.redirect(flask.url_for('upload'))
    
# end photo uploading code
@app.route('/MyPhoto/', methods=['GET', 'POST'])
@flask_login.login_required
def myphoto():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    pid = request.form.get('picture_id')
    photos=getUsersPictures(uid)
    if request.method == 'GET':
        return render_template('MyPhoto.html', name=flask_login.current_user.id, photos=photos)
    else:
        like = request.form.get('like')
        if check_like(pid,uid) == False:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Likes (picture_id, user_id) VALUES ('{0}', '{1}')".format(pid, uid))
            conn.commit()
            if like == 'yes' and photolike(pid, uid):
                return render_template('MyPhoto.html', message="You have liked this photo", photos=photos)
            else:
                return render_template('MyPhoto.html', message="uncommon action", photos=photos)
        else:
            return render_template('MyPhoto.html', message="Unable to like again", photos=photos)


@app.route('/AllPhotos/', methods=['GET', 'POST'])
@flask_login.login_required
def allphotos():
    #user_id = getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(picture_id), imgdata, caption FROM Pictures")
    photos=cursor.fetchall()
    #NOTE list of tuples, [(imgdata, pid), ...]
    if request.method == 'GET':
        return render_template('AllPhotos.html', photos=photos)
    else:
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        text = request.form.get('text')
        like = request.form.get('like')
        date=request.form.get('date')
        picture_id = request.form.get('picture_id')
        if like == 'yes':
            if photolike(picture_id, user_id):
                if text:
                    if isPictureBelongtoUser(picture_id, user_id):
                        return render_template('AllPhotos.html', message="You cannot comment under your own photo and you have liked this photo", photos=photos)
                    else:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Comments (text, picture_id, user_id, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(text, picture_id, user_id, date))
                        conn.commit()
                        return render_template('AllPhotos.html', message="Comment added: " + text, photos=photos)
                else:
                    return render_template('AllPhotos.html', photos=photos)
            else:
                if text:
                    if isPictureBelongtoUser(picture_id, user_id):
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Likes (picture_id, user_id) VALUES ('{0}', '{1}')".format(picture_id, user_id))
                        conn.commit()
                        return render_template('AllPhotos.html', message="Cannot comment own photo but like this photo", photos=photos)
                    else:
                        cursor = conn.cursor()
                        cursor.execute("INSERT INTO Comments (text, picture_id, user_id, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(text, picture_id, user_id, date))
                        cursor.execute("INSERT INTO Likes (picture_id, user_id) VALUES ('{0}', '{1}')".format(picture_id, user_id))
                        conn.commit()
                        return render_template('AllPhotos.html', message="Like this photo and comment added: " + text, photos=photos)
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Likes (picture_id, user_id) VALUES ('{0}', '{1}')".format(picture_id, user_id))
                    conn.commit()
                    return render_template('AllPhotos.html', message="Like this photo", photos=photos)
        else:
            if text:
                if isPictureBelongtoUser(picture_id, user_id) and photolike(picture_id, user_id):
                    return render_template('AllPhotos.html', message="You cannot comment under your own photo and you have liked this photo", photos=photos)
                else:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO Comments (text, picture_id, user_id, date) VALUES ('{0}', '{1}', '{2}', '{3}')".format(text, picture_id, user_id, date))
                    conn.commit()
                    return render_template('AllPhotos.html', message="Comment added: " + text, photos=photos)
            else:
                return render_template('AllPhotos.html', photos=photos)


@app.route('/deletealbums/', methods=['GET', 'POST'])
@flask_login.login_required
def deleteAlbums():
    if request.method == 'GET':
        uid=flask_login.current_user.id
        album_id=getUsersAlbums(getUserIdFromEmail(flask_login.current_user.id))
        if not album_id:
            return render_template("profile.html", message='You have no albums')
        else:
            return render_template("profile.html", message='You have these albums', viewAlbums=album_id)
    else:
        user_email=flask_login.current_user.id
        user_id=getUserIdFromEmail(user_email)
        albumlist=getUsersAlbums(user_id)
        album_id = request.form.get('album_id')
        cursor = conn.cursor()
        cursor.execute("SELECT album_id FROM Albums WHERE album_name = '{0}'".format(album_id))
        album_id = int(str(album_id).strip("()").split(",")[0])
        ids = []
        for i in range(len(albumlist)):
            ids.append(int(albumlist[i][0]))
        if not albumlist:
            return render_template("profile.html", message='You have no album')
        elif album_id not in ids:
            return render_template("profile.html", message='You do not have such album')
        else:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Albums WHERE album_id={0}".format(album_id))
            cursor.execute("DELETE FROM Pictures WHERE album_id={0}".format(album_id))
            conn.commit()
            albumlist=getUsersAlbums(user_id)
            return render_template("CreateAlbum.html", message='You have these albums', viewAlbums=albumlist)

@app.route('/deletephoto/', methods=['GET', 'POST'])
@flask_login.login_required
def deletePhoto(): 
    user_id=getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(picture_id), imgdata, caption FROM Pictures")
    photos=cursor.fetchall()
    print(photos)
    if request.method == 'GET':
        return render_template("MyPhoto.html", photos=photos)
    else:
        delete = request.form.get('delete')
        picture_id = request.form.get('picture_id')
        print(picture_id)
        print('user_id ',user_id)
        if delete =='yes':
            cursor = conn.cursor()
            cursor.execute("DELETE FROM Pictures WHERE picture_id={0}".format(picture_id))
            cursor.execute("SELECT DISTINCT(picture_id), imgdata, caption FROM Pictures")
            photos=cursor.fetchall()
            conn.commit()
            return render_template("profile.html",message = "delete complete",photos=photos)
        else:
            return render_template("MyPhoto.html", message = "You cannot delete photo that does not belong to you",photos = photos)


@app.route('/friend/', methods=['GET', 'POST'])
@flask_login.login_required
def view_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    print("UserID", uid)
    friendList = getFriendList(int(uid))
    message = 'lets view your friends'  # send as a part of render
    # uid = 0

    friendList = [int(x[0]) for x in friendList]

    friend_name_list = [getUserName(friend) for friend in friendList]
    if len(friend_name_list) == 0:
        friend_name_list = [" "]
    else:
        friend_name_list = [friend[0][0] + " " + friend[0][1] for friend in friend_name_list]

    print(friend_name_list)

    new_friend_email = request.form.get('new email')

    if new_friend_email:

        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM Users WHERE email = '{0}'".format(new_friend_email))
        result = cursor.fetchall()

        print(len(result))

        if len(result) == 0 or int(result[0][0]) == int(uid):
            print("user not found")
            return render_template('friend.html', message="user not found", viewFriends=friend_name_list)

        new_friend_id = int(result[0][0])
        print("new friend's id is ", new_friend_id)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO Friends (user_id, user_id2) VALUE ('{0}','{1}')".format(int(uid), new_friend_id))
        cursor.execute("INSERT INTO Friends (user_id, user_id2) VALUE ('{0}','{1}')".format(new_friend_id, int(uid)))
        conn.commit()

        print("add successful")
        message = ("successfully add ", getUserName(new_friend_id)[0])

    return render_template('friend.html', message=message, viewFriends=friend_name_list)

@app.route('/VisComment/', methods=['GET','POST'])
def visitorComment():
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(picture_id), imgdata, caption FROM Pictures")
    photos=cursor.fetchall()
    if request.method == 'GET':
        return render_template('visitors.html', photos=photos)
    else:
        text = request.form.get('text')
        date=request.form.get('date')
        picture_id = request.form.get('picture_id')
        if text:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Comments (text, picture_id, date) VALUES ('{0}', '{1}', '{2}')".format(text, picture_id, date))
            conn.commit()
            return render_template('visitors.html', message="Comment added: " + text, photos=photos)
        else:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO Likes (picture_id,user_id) VALUES ('{0}','{1}')".format(picture_id,user_id))
            conn.commit()
            return render_template('visitors.html', photos=photos)




@app.route('/listtag/', methods=['GET','POST'])
@flask_login.login_required
def listByTags():
    tag = request.args['tag']
    user_id=getUserIdFromEmail(flask_login.current_user.id)
    photos = getUsersPhotos_Tags(user_id, tag)
    return render_template("tags.html", message="tag: " + str(tag)+" has these photos", photos=photos)

@app.route('/tags/', methods=['GET','POST'])
@flask_login.login_required
def Tags():
    user_id=getUserIdFromEmail(flask_login.current_user.id)
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM Associate GROUP BY word ORDER BY COUNT(*) DESC")
    tags = cursor.fetchall()

    if request.method =='GET':
        return render_template('tags.html', message="Top Tags: ", tags = tags)
    else:
        tag = request.form.get('word')
        print("tag ",tag)
        type = request.form.get('type')
        taglst = tag.split(" ")
        photolist = []
        if type == "myphoto":
            for t in taglst:
                photolist=getUsersPhotos_Tags(user_id,t)
        else:
            for t in taglst:
                photolist=getTagPhotos(t)
        print(photolist)
        return render_template('tags.html',photos = photolist, message="Here are photos", tags = tags)

@app.route('/PopComment/', methods=['GET','POST'])
@flask_login.login_required
def PopComment():
    cursor = conn.cursor()
    cursor.execute("SELECT text FROM Comments;")
    comments = cursor.fetchall()

    if request.method =='GET':
        return render_template('PopComment.html', message="All comments: ", comments = comments)
    else:
        comment = request.form.get('comment')
        check = commentINtext(comment)
        print(check)
        if check == True:
            cursor = conn.cursor()
            cursor.execute("SELECT text FROM Comments;")
            comments = cursor.fetchall()
            return render_template('PopComment.html',photos = photoCom(comment), message="Here are photos", comments = comments)
        return render_template('PopComment.html',photos = photoCom(comment), message="Here are photos", comments = comments)

def photoCom(comment):
    cursor = conn.cursor()
    cursor.execute("SELECT P.picture_id, P.imgdata ,P.caption FROM Comments AS C, Pictures AS P WHERE C.picture_id = P.picture_id AND C.text = '{0}'".format(comment))
    return cursor.fetchall()


def commentINtext(comment):
    cursor = conn.cursor()
    p = cursor.execute("SELECT text FROM Comments AS C Where C.text ='{0}'".format(comment))
    print(p)
    if p:
        return True
    else:
        return False




def countContribution():
    cursor = conn.cursor()
    cursor.execute("CREATE TEMPORARY TABLE t1 AS (SELECT user_id, COUNT(picture_id) AS n FROM Pictures GROUP BY user_id);")
    cursor.execute("CREATE TEMPORARY TABLE t2 AS (SELECT user_id, COUNT(comment_id) AS n FROM Comments GROUP BY user_id);")
    cursor.execute("CREATE TEMPORARY TABLE t3 AS SELECT user_id, n FROM t1 UNION ALL SELECT user_id, n FROM t2 GROUP BY user_id, n;")

    cursor.execute("SELECT user_id , sum(n) FROM t3 WHERE user_id > 0 GROUP BY user_id ORDER BY sum(n) DESC;")
    
    users=cursor.fetchall()
    cursor.execute("DROP TABLE t1,t2,t3;")
    
    
    return users

@app.route('/userActivity', methods=['GET'])
def userActivity(): #NOTE list of tuples, [(imgdata, pid), ...]
    contribution=countContribution()[0:10]
    return render_template("userActivity.html", users = contribution,message='Welecome to User Activity')


def getTagPhotos(tag):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(P.picture_id), P.imgdata, P.caption FROM Associate AS A, Pictures AS P WHERE A.picture_id = P.picture_id AND A.word = '{0}'".format(tag))
    return cursor.fetchall()

def getUsersPhotos_Tags(uid, tag):
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT(P.picture_id), P.imgdata ,P.caption FROM Associate AS A, Pictures AS P WHERE A.picture_id = P.picture_id AND P.user_id = '{0}' AND A.word = '{1}'".format(uid, tag))
    return cursor.fetchall() 

def userToptag(user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT word FROM Associate where user_id={0} GROUP BY tag ORDER BY COUNT(*) DESC".format(user_id))
    return cursor.fetchall()

@app.route('/recommondfriend/', methods=['GET', 'POST'])
@flask_login.login_required
def recom_friends():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    print("UserID", uid)
    friendList = getrecommondFriendList(int(uid))
    print(friendList)
    message = 'lets view your friends'  # send as a part of render
    # uid = 0
    nodup = list(set(friendList))
    print(nodup)
    cl = []
    for i in nodup:
        c = 0
        for j in friendList:
            if j == i:
                c += 1
            else:
                c += 0
        cl += [(i,c)]
    cl = dict(cl)
    test = sorted(cl.items(),key = lambda (k,v):(v,k),reverse = True)
    print("t",test)
    #cl = [key for (key,value) in sorted(dict(cl).items(),reverse = True)]
    #print(cl)

    friend_name_list = [getUserName(friend[0]) for friend in test]
    print(friend_name_list)
    #print(friend_name_list)
    if len(friend_name_list) == 0:
        friend_name_list = [" "]
    else:
        friend_name_list = [friend[0][0] + " " + friend[0][1] for friend in friend_name_list]

    return render_template('recommondfriend.html', message=message, viewFriends=friend_name_list)

# default page
@app.route("/", methods=['GET'])
def hello():
    return render_template('profile.html', message='Welecome to Photoshare')

@app.route('/detail', methods=['GET'])
def MoreDetails():
    picture_id = request.args['detail']
    likes = countLikes(picture_id)
    Userslike = listLikeUsers(picture_id)
    comments=listComments(picture_id)
    if likes:
        return render_template("AllPhotos.html", message="This photo has " + str(likes[0][0]) + " likes", comments=comments, Userslike=Userslike )
    else:
        return render_template("AllPhotos.html", message="This photo has no like", comments=comments)

def countLikes(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Likes WHERE picture_id = '{0}' GROUP BY picture_id".format(picture_id))
    return cursor.fetchall()

def listComments(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT text, user_id, date FROM Comments WHERE picture_id='{0}'".format(picture_id))
    return cursor.fetchall()

def listLikeUsers(picture_id):
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM Likes WHERE picture_id='{0}'".format(picture_id))
    return cursor.fetchall()

if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
