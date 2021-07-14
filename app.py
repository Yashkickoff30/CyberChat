import pickle
import pyrebase as pb
from config import config
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
from tensorflow.python.keras.backend import set_session
from tensorflow.python.keras.models import load_model
from analyzer import analyzeUserSentiment
from flask_socketio import *
from flask import Flask, render_template, request, session, url_for, redirect
import warnings
warnings.filterwarnings('ignore')
firebaseConfig = config
firebase = pb.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vnkdjnfjknfl1232#'
socketio = SocketIO(app)

sess = tf.Session()
graph = tf.get_default_graph()

set_session(sess)
model = load_model('second_iter.hdf5')
with open('tokenizer.pickle', 'rb') as handle:
    tokenizer = pickle.load(handle)

error_code = 0
userList = {}
chatData = {}


def toxicity_detector(name, string):
    prediction_result = {}
    tags = []
    print(name + ' : ' + string)
    new_text = [string]
    new_text = tokenizer.texts_to_sequences(new_text)
    new_text = pad_sequences(new_text, maxlen=1500)
    global graph
    global sess
    with graph.as_default():
        set_session(sess)
        prediction = model.predict(new_text)
        toxic = round((prediction[0][0] * 100), 2)
        s_toxic = round((prediction[0][1] * 100), 2)
        obs = round((prediction[0][2] * 100), 2)
        threat = round((prediction[0][3] * 100), 2)
        insult = round((prediction[0][4] * 100), 2)
        hate = round((prediction[0][5] * 100), 2)
        result = round((toxic + obs + insult + hate) / 4, 2)
        print('Result: {}'.format(result))
        prediction_result['score'] = round(result)
        if result > 50:
            print('Offensive comment detected')
            prediction_result['final_verdict'] = 'Offensive Comment Detected'
            print('Tags related to your offensive comments: ')
            tags = findTags(obs, insult, hate, threat, tags)
            prediction_result['tags'] = tags
            prediction_result['total_tags'] = len(tags)
        else:
            print('Good Job! No Offensive comment detected')
            tags = findTags(obs, insult, hate, threat, tags)
            prediction_result['final_verdict'] = 'Good Job! No Offensive comment detected'
            prediction_result['tags'] = tags
            prediction_result['total_tags'] = len(tags)
            print()
        if False:
            print('Given String   {:}'.format(string))
            print('Toxic:         {:}%'.format(round(toxic)))
            print('Severe Toxic:  {:}%'.format(round(s_toxic)))
            print('Obscene:       {:}%'.format(round(obs)))
            print('Threat:        {:}%'.format(round(threat)))
            print('Insult:        {:}%'.format(round(insult)))
            print('Identity Hate: {:}%'.format(round(hate)))
            print('Result:        {:}%'.format(result))
        return prediction_result


def findTags(obs, insult, hate, threat, tags):
    if round(obs) >= 45:
        print('Obscene ')
        tags.append('Obscene')
    if round(insult) >= 35:
        print('Insult')
        tags.append('Insult')
    if round(hate) >= 30:
        print('Hate Speech')
        tags.append('Hate Speech')
    if round(threat) >= 20:
        print('Threat')
        tags.append('Threat')
    return tags


def saveUserMessage(name, message):
    if name not in chatData.keys():
        chatData[name] = []
    if name in chatData.keys():
        chatData[name].append(message)
    print(chatData)

# ERROR CODES:
#  0 --> No error
# 1 --> Invalid username or password (LOGIN)
# 2 --> Password doesn't match (SIGNUP)
# 3 --> Username already exists (SIGNUP)
# 4 --> Password less than 6 characters. (SIGNUP)


@app.route('/', methods=['POST', 'GET'])
def home():
    global error_code
    if flask.request.method == 'GET':
        error_code = 0
        print('[ERROR CODE IS ....]' + str(error_code))
        return render_template('home.html', error=error_code)
    else:
        username = request.form.get('username1')
        email = request.form.get('signupemail1')
        password = request.form.get('signuppass1')
        confirm_password = request.form.get('signconfirm1')
        session_count = 0
        print(username)
        print(email)
        print(password)
        print(confirm_password)
        if len(password) >= 6:
            if password == confirm_password:
                try:
                    auth.create_user_with_email_and_password(email, password)
                    print("Successfully signed in!!")
                    x = email.find("@")
                    email_trim = email[:x]
                    db_jsondata = {"name": username, "session": session_count}
                    db.child("users").child(email_trim).set(db_jsondata)
                    error_code = 0  # No error.
                    print('[ERROR CODE IS ....]' + str(error_code))
                    return render_template('home.html', error=error_code)
                except:
                    error_code = 3  # Username Already exist.
                    print('[ERROR CODE IS ....]' + str(error_code))
                    return render_template('home.html', error=error_code)
            else:
                error_code = 2  # Passwords doesn;t match.
                print('[ERROR CODE IS ....]' + str(error_code))
                return render_template('home.html', error=error_code)
        else:
            error_code = 4  # Password lesser than 6 chars.
            print('[ERROR CODE IS ....]' + str(error_code))
            return render_template('home.html', error=error_code)


@app.route('/index', methods=['POST', 'GET'])
def index():
    if flask.request.method == 'GET':
        return render_template('index.html')
    elif flask.request.method == 'POST':
        login_email = request.form.get('email')
        login_password = request.form.get('password')
        print(login_email)
        print(login_password)
        try:
            auth.sign_in_with_email_and_password(login_email, login_password)
            error_code = 0  # No error.
            print("Successfully logged in!!")
            x = login_email.find("@")
            email_trim = login_email[:x]
            print("The trimmed email is", email_trim)
            # session['email'] = email_trim
            session_dbdata = db.child("users").child(
                email_trim).child("session").get().val()
            print(session_dbdata)
            session_dbdata += 1
            db.child("users").child(email_trim).update(
                {"session": session_dbdata})
            return render_template('index.html',email=login_email)
        except:
            error_code = 1  # Invalid Username and password.
            print("Invalid username or password!!")
            print('[ERROR CODE IS ....]' + str(error_code))
            return render_template('home.html', error=error_code)

# {
#   username : mental_state / session_count,
# }


@app.route('/chat')
def chat_page():
    username = request.args.get('username')
    org_email = request.args.get('email')
    x = org_email.find("@")
    email_trim = org_email[:x]
    print("The email from home page is", org_email)
    session['username'] = username
    session_count = db.child("users").child(
        email_trim).child("session").get().val()
    # print(session['email'])
    if session_count > 1:
        mental_state = db.child("users").child(
            email_trim).child("mentalstate").get().val()
        print(mental_state/session_count)
        print(round(mental_state/session_count))
        if username not in userList.keys():
            userList[username] = round(mental_state/session_count)
    else:
        userList[username] = 999
    return render_template('chatpage.html', username=session['username'],email=org_email)


@app.route('/leave')
def leave():
    return redirect(url_for('index'))


@socketio.on('message')
def handle_client_message(data):
    # print(str(data))
    saveUserMessage(data['user'], data['msg'])
    res = toxicity_detector(data['user'], data['msg'])
    data['result'] = res
    emit('message', data, broadcast=True)


@socketio.on('joined')
def init_message(data):
    # print('Sending INIT MESSAGE........')
    # print(userList)
    emit('status', {
        'user': 'ChatBot',
        'msg': session['username'] + ' has entered the chat!',
    }, broadcast=True, include_self=False)
    emit('init_message', {
        'user': 'ChatBot',
        'msg': 'Welcome to Cyber Chat!',
    })
    # print("[sending user list......]")
    emit('userlist', userList, broadcast=True)


@socketio.on('leave')
def user_left(data):
    # print(data['user'] + ' has left the session')
    email = data['email']
    x = email.find("@")
    email_trim = email[:x]
    userList.pop(data['user'])
    emit('init_message', {
        'user': 'ChatBot',
        'msg': data['user'] + ' has left the chat',
    }, broadcast=True, include_self=False)
    #{'verdict': 'neutral', 'username': 'eash', 'tp': 0, 'tneg': 0, 'tneu': 3, 'tcomp': 0}
    #{'eash': ['hii', 'hello', 'how r u?']}
    userName = data['user']
    if userName not in chatData.keys():
        chatData[userName] = []
    print(userName)
    print(chatData)
    print(len(chatData[userName]))
    if(len(chatData[userName]) > 0):
        userResult = analyzeUserSentiment(data['user'], chatData)
    else:
        userResult = {
            'verdict': 'neutral',
            'username': userName,
            'tp': 0,
            'tneg': 0,
            'tneu': 0,
            'tcomp': 0
        }
    print(userResult)
    emit('userResult', userResult)
    # print('RESULT EMIT SUCCESSFULLY')
    emit('userlist', userList, broadcast=True)
    #print(session['email'])
    print("Session Username:",email_trim)
    session_count = db.child("users").child(
        email_trim).child("session").get().val()
    if session_count > 1:
        mentalstate = db.child("users").child(
            email_trim).child("mentalstate").get().val()
        mentalstate += userResult['tcomp']
        mentalstate_dbdata = {"mentalstate": mentalstate}
        print("Mental state is:",mentalstate_dbdata)
    else:
        mentalstate_dbdata = {"mentalstate": userResult['tcomp']}
        print("Mental state is:",mentalstate_dbdata)
    db.child("users").child(email_trim).update(mentalstate_dbdata)


if __name__ == '__main__':
    socketio.run(app, port=3000, debug=True)
