from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from external.crystalpay_sdk import *
from dotenv import load_dotenv
import os

load_dotenv()
login = os.getenv('login')
secret_1 = os.getenv('secret_1')
secret_2 = os.getenv('secret_2')
crystalpayAPI = CrystalPAY(login, secret_1, secret_2)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer)
    text = db.Column(db.Text)
    isActive = db.Column(db.Boolean, default=True)
 
with app.app_context():
    db.create_all()

@app.route('/')
def main_page():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        title = request.form['title']
        price = request.form['price']
        text = request.form['text']
        item = Item(title=title, price=price, text=text)
        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            return f'Ошибка {e}'
    else:
        return render_template('create.html')
    
@app.route('/buy/<int:id>')
def buy_course(id):
    course = Item.query.get(id)
    create_purchase = crystalpayAPI.Invoice.create(course.price, InvoiceType.purchase, 15, description='Покупка курса', redirect_url='http://127.0.0.1:5000/')
    
    return redirect(create_purchase['url'])

if __name__ == '__main__':
    app.run(debug=True)