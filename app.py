from flask import Flask, render_template, request, redirect, url_for, session as login_session
import pyrebase

Config = {
  "apiKey": "AIzaSyBomXJXsjnb7Oa0nnSPxb5Sx4TRwuK7tss",
  "authDomain": "kibo-381a6.firebaseapp.com",
  "projectId": "kibo-381a6",
  "storageBucket": "kibo-381a6.appspot.com",
  "messagingSenderId": "784584583203",
  "appId": "1:784584583203:web:e530ae6db2df93594de996",
  "measurementId": "G-EE2NX027Y7",
  "databaseURL":"https://kibo-381a6-default-rtdb.europe-west1.firebasedatabase.app/"
}

app = Flask(__name__, template_folder="templates", static_folder="static")
app.config['SECRET_KEY'] = 'Your_secret_string'
firebase = pyrebase.initialize_app(Config)
db = firebase.database()
auth = firebase.auth()

@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            login_session['user'] = user
            user_data = {"email": email, "password": password}
            UID = login_session['user']['localId']
            db.child("users").child(UID).set(user_data)
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            return "Registration failed, please try again."
    return render_template('register.html')

@app.route('/profile', methods=['GET'])
def profile():
    if 'user' not in login_session:
        return redirect(url_for('login'))
    
    user_id = login_session['user']['localId']
    user_data = db.child("users").child(user_id).get().val()
    keys = db.child("contacts").child(user_id).get().val()
    
    # your_requests = {}
    # if keys:
    #     for key, val in keys.items():
    #         if key == user_id:
    #             uid = val
    #             break

    return render_template('profile.html', contacts=keys, user=user_data, uid = login_session['user']['localId'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            login_session['user'] = user
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            return render_template('login.html')
    return render_template('login.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    instructors = db.child("instructors").get().val()
    print(instructors)
    if instructors is None:
        instructors = {}
    return render_template('index.html', instructors=instructors)

@app.route('/update_request/<uid>/<key>', methods=['GET', 'POST'])
def update_request(uid, key):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']

        db.child("contacts").child(uid).child(key).update({"name": name, "email": email, "message": message})
        return redirect(url_for('profile'))

    request_data = db.child("contacts").child(uid).child(key).get().val()

    name_before = request_data['name']
    email_before = request_data['email']
    message_before=request_data['message']
    return render_template('update_request.html', key = key,user_id = uid,  request_data=request_data, name = name_before, email = email_before, message = message_before)


@app.route('/delete_request/<uid>/<key>')
def delete_request(uid, key):
    db.child("contacts").child(uid).child(key).remove()
    return redirect(url_for('profile'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        UID = login_session['user']['localId']
        db.child("contacts").child(UID).push({"name": name, "email": email, "message": message})
        return redirect(url_for('home'))
    return render_template('contact.html')

@app.route('/easter_egg')
def easter_egg():
    return render_template('easter_egg.html')

@app.route('/easter_egg1')
def easter_egg1():
    return render_template('easter_egg1.html')

@app.route('/admin')
def admin():
    all_contacts = db.child("contacts").get().val()
    contacts = {}

    if all_contacts:
        for uid, user_contacts in all_contacts.items():
            for key, contact in user_contacts.items():
                contacts[key] = {
                    'uid': uid,
                    'name': contact.get('name'),
                    'email': contact.get('email'),
                    'message': contact.get('message')
                }
    
    return render_template('admin.html', contacts=contacts)



if __name__ == '__main__':
    app.run(debug=True)
