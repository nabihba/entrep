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
    keys = db.child("contacts").get().val()
    
    your_requests = {}
    if keys:
        for key, val in keys.items():
            if key == user_id:
                your_requests = val
                break
    
    return render_template('profile.html', user=user_data, contacts=your_requests)

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

@app.route('/update_request/<request_id>', methods=['GET', 'POST'])
def update_request(request_id):
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        db.child("contacts").child(request_id).update({"name": name, "email": email, "message": message})
        return redirect(url_for('profile'))
    
    request_data = db.child("contacts").child(request_id).get().val()
    return render_template('update_request.html', request_data=request_data, request_id=request_id)


@app.route('/delete_request/<request_id>')
def delete_request(request_id):
    db.child("contacts").child(request_id).remove()
    return redirect(url_for('profile'))

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        UID = login_session['user']['localId']
        db.child("contacts").child(UID).set({"name": name, "email": email, "message": message})
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
    contacts = db.child("contacts").get().val()
    if not contacts:
        contacts = {}
    return render_template('admin.html', contacts=contacts)

@app.route('/add_instructor', methods=['GET', 'POST'])
def add_instructor():
    name = request.form['name']
    description = request.form['description']
    instructor = {"name": name, "description": description}
    db.child("instructors").push(instructor)
    return redirect(url_for('home'))

@app.route('/edit_instructor/<id>', methods=['GET', 'POST'])
def edit_instructor(id):
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        db.child("instructors").child(id).update({"name": name, "description": description})
        return redirect(url_for('home'))
    instructor = db.child("instructors").child(id).get().val()
    return render_template('edit_instructor.html', instructor=instructor, id=id)

@app.route('/delete_instructor/<id>', methods=['GET', 'POST'])
def delete_instructor(id):
    db.child("instructors").child(id).remove()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
