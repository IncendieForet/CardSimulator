from flask import Flask, render_template, flash, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm.attributes import flag_modified
import random, requests

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///user.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    tir = db.Column(db.Integer,default=30)
    cards = db.Column(JSON,default=list)

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route("/set_tir", methods = ['POST'])
def set_tir():
    if session.get('id'):
        user=User.query.filter_by(id=session.get('id')).first()
        user.tir=max(user.tir,30)
        db.session.commit()
        return '', 204
    
@app.route('/tirage', methods = ['POST'])
def tirage():
    data = request.json
    tb = []
    session.pop('images', None)
    user = User.query.filter_by(id=session.get('id')).first()
    user.cards = user.cards or []
    for i in range(data['counter']):
        cmax = requests.get('https://api.tcgdex.net/v2/fr/cards').json()
        nb = random.randint(0,len(cmax))
        while 'image' not in cmax[nb]:
            nb = random.randint(0,len(cmax))
        tb.append({'name':cmax[nb]['name'],'src':f"{cmax[nb]['image']}/high.png"})
        user.cards.append({'name':cmax[nb]['name'],'src':f"{cmax[nb]['image']}/high.png"})
    user.tir -= data['counter']
    flag_modified(user,"cards")
    db.session.commit()
    session['images'] = tb
    return redirect(url_for('get_tirages'))

@app.route('/tirages')
def get_tirages(): 
    if session.get('images', []) != []:
        return render_template('tirages.html', images=session.get('images', []))
    return redirect(url_for('index')) 

@app.route('/delete',methods=['POST'])
def delete_cards():
    data=request.json
    user=User.query.filter_by(id=session.get('id')).first()
    user.cards = user.cards or []
    if len(data['delcards'])==len(user.cards):
        user.cards.clear()
    else:
        user.cards = [
        card for i,card in enumerate(user.cards)
        if i not in data['delcards']
    ]
    user.tir+=len(data['delcards'])//2
    flag_modified(user,"cards")
    db.session.commit()
    return redirect(url_for('collection'))

@app.route('/favorite',methods=['POST'])
def favorite_card():
    data=request.json
    user=User.query.filter_by(id=session.get('id')).first()
    user.cards = user.cards or []
    item=user.cards.pop(data['index'])
    user.cards.insert(0,item)
    flag_modified(user,"cards")
    db.session.commit()
    return redirect(url_for('collection'))

@app.route("/collections")
def all_collections():
    if session.get('id'):
        userc=[]
        with app.app_context():
            for user in User.query.all():
                if not user.cards:
                    userc.append({'name':user.username,'length':len(user.cards)})
                else:
                    userc.append({'name':user.username,'length':len(user.cards),'favorite':user.cards[0]})
            return render_template('collections.html',collections=userc)
    return redirect(url_for('index'))

@app.route("/getcol", methods = ['POST'])
def gotocoll():
    data=request.json
    selected_user=User.query.filter_by(username=data['name']).first()
    if session.get('id')==selected_user.id:
        return redirect(url_for('collection'))
    session['visitor'] = selected_user.cards
    return redirect(url_for('go_to_visitor'))

@app.route('/visitor')
def go_to_visitor():
    if session.get('visitor') is not None:
        return render_template('visitor.html',visitorcards=session.get('visitor'))
    return redirect(url_for('index'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash,password):
            session['id'] = user.id
            return redirect(url_for('home'))
        else:
            flash("Mot de passe incorrect ❌")
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm_password']
        if password != confirm:
            flash("Les mots de passe ne correspondent pas ❌")
            return redirect(url_for('register'))
        if username.isalnum() and User.query.filter_by(username=username).first():
            flash("Username déjà utilisé ❌")
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password_hash=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        session['id'] = new_user.id
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/collection')
def collection(user = None):
    if session.get('id'):
        user=db.session.get(User, session.get('id'))
        return render_template('collection.html',images=user.cards)
    return redirect(url_for('index'))

@app.route('/home')
def home(user = None):
    if session.get('id'):
        user=db.session.get(User, session.get('id'))
        user.cards = user.cards or []
        if not user.cards:
            return render_template('home.html',user=user)
        return render_template('home.html',user=user,favorite_card=user.cards[0])
    return redirect(url_for('index'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)