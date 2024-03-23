from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from external.crystalpay_sdk import *
from dotenv import load_dotenv
import os

load_dotenv()
login = os.getenv('login')
secret_1 = os.getenv('secret_1')
secret_2 = os.getenv('secret_2')
mysql_login = os.getenv('mysql_login')
mysql_password = os.getenv('mysql_password')
host = os.getenv('host')
db_name = os.getenv('db_name')
crystalpayAPI = CrystalPAY(login, secret_1, secret_2)

application = Flask(__name__)
application.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{mysql_login}:{mysql_password}@{host}/{db_name}'
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(application)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer)
    text = db.Column(db.Text)
    prod_url = db.Column(db.Text)
    isActive = db.Column(db.Boolean, default=True)
 
with application.app_context():
    db.create_all()

@application.route('/')
def main_page():
    items = Item.query.order_by(Item.price).all()
    return render_template('index.html', data=items)

@application.route('/about')
def about():
    return render_template('about.html')

@application.route('/create', methods=['POST', 'GET'])
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
    

@application.route('/buy/<int:id>')
def buy_course(id):
    course = Item.query.get(id)
    create_purchase = crystalpayAPI.Invoice.create(course.price, InvoiceType.purchase, 15, description='Покупка курса', redirect_url=f'{course.prod_url}')
    
    return redirect(create_purchase['url'])

if __name__ == '__main__':
    application.run(debug=True)