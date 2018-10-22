from flask import Flask, request, redirect, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy 
import re

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "ads;lkfja"

class Blogpost(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner = db.Column(db. Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    owner = db.relationship('Blogpost', backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():
    blogs=Blogpost.query.all()
    blog_id = request.args.get('id')
    

    if blog_id:
        post = Blogpost.query.get(blog_id)
        return render_template('blog-ID.html', title="Blog Post", post=post)    
    else:
 
        return render_template('blogs.html', blogs=blogs)

@app.route('/newpost', methods=['POST', 'GET'])
def newpost(): 
    if request.method == 'POST':   
        title = request.form['title']
        body = request.form['body']
        user = User.query.filter_by(username=session['user']).all()

        new_blog = Blogpost(title, body, user)
        db.session.add(new_blog)
        db.session.commit()

        if (title) or (body) == "":
            return redirect('/blogs')
        else:
            flash('Fields cannot be left empty.')
    else:
        return render_template('newpost.html')    
 
@app.route('/signup', methods=['POST', 'GET']) 
def signup():

    username_error = ''
    password_error = ''
    verify_password_error = ''
    email_error = ''
    email_regex = re.compile(r"[^@\s]+@[^@\s]+\.[a-zA-Z0-9]+$")

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
        email = request.form['email']
    
    
        if (len(username) < 3 or len(username) > 20) or (" " in username):
            
            username_error = 'Invalid entry.  This field must contain between 3-20 alpha-numeric characters with no spaces.'
            username = ''

        if (len(password) < 3 or len(password) > 20) or (" " in password):
            password_error = 'Invalid entry.  This field must contain between 3-20 alpha-numeric characters with no spaces.'
            password = ''

        if verify_password != password:
            verify_password_error = 'Your passwords do not match.'
            verify_password = ''

        if not email_regex.match(email): 
            email_error = 'Invalid E-mail.'
        if email != '' and (len(email) < 3 or len(email) > 20):
            email_error = 'Your email is outside the limits of 3 - 20 characters.'
    
    
        if not username_error and not password_error and not verify_password_error and not email_error:
            #user = username
            new_user=User(username, password)
            db.session.add(new_user)
            db.session.commit()
            flash('new user added')
            return redirect('/')   

#        return render_template('user-signup.html', username_error=username_error,
#            password_error=password_error, verify_password_error=verify_password_error,
#            email_error=email_error, username=username, password=password, verify_password=verify_password, email=email, )        
            


        return redirect('/login')

    return render_template('user-signup.html', username_error=username_error,
        password_error=password_error, verify_password_error=verify_password_error,
        email_error=email_error, username='', password='', verify_password='', email='' )        

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if not user:
            flash ('user not found')

            return redirect('/login')
            
        if user and user.password == password:
            session['user']=username
            return redirect('/')
    
    return render_template('login.html')

@app.route('/Sign_Out')
def Sign_Out():
    del session['user']
    return redirect('/')    

if __name__ == '__main__':
    app.run()