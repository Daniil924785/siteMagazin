from flask import Flask, render_template, request, redirect,send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os
from cloudipsp import Api, Checkout # библиотека для работы с денежными переводами

app = Flask(__name__) # создание связи с бд
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)



class Item(db.Model): # таблица товаров
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    isActive = db.Column(db.Boolean, default=True)


class Regist(db.Model):# таблица для регистрации пользователя
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), default=False)
    telefone = db.Column(db.String(50), default=False)
    adress = db.Column(db.String(150), nullable=False)

    def __repr__(self): #Вывод записей без данной функции вывод сообщений будет не корректен пример  Item 1
        return self.title




@app.route('/') # главная старница
def index():
    return render_template('index.html')

@app.route('/registration') # страница регистрации
def registration():
    return render_template('registration.html')

@app.route('/thing') # страница товары и данные на странице отсортерованы по номеру id в таблице бд
def thing():
    items = Item.query.order_by(Item.id).all()
    return render_template('thing.html', items=items)

@app.route('/thing/<int:id>') # таблица информация о товаре.Данная строка нужна для того что бы мы переходина на нажатую нами страницу товара
def detail(id):
    item = Item.query.get(id)#так как нам нужна информация о том товаре на который мы нажали нам нужен его id
    return render_template('detail.html', item=item)


@app.route('/thing/<int:id>/del') #
def  delete(id):
    item = Item.query.get_or_404(id)#данная строчка обозначает если не будет найден id выдаст ошибку 404
    try:
        db.session.delete(item)# создается сессия с БД и происходит процесс удаления
        db.session.commit() #доба
        return redirect('/') # после удаления перекидывает на главную странцу
    except:
        return "При удалении статьи произошла ошибка"

@app.route('/thing/<int:id>/update', methods=['POST', 'GET']) # страничка редактирования
def update(id):
    item = Item.query.get(id) #происходит поиск нужного нам товара
    if request.method == "POST":
        item.title = request.form['title']#затем происходит замена изначальной формы товара
        item.price = request.form['price']

        try:
            db.session.commit()
            return redirect('/thing')
        except:
            return "При редактировании товара произошла ошибка"
    else:
        return render_template('thing_update.html',item=item)

@app.route('/about')#стараничка про магазин
def about():
    return render_template('about.html')

@app.route('/buy/<int:id>')#страничка покупки
def item_buy(id):#
    item = Item.query.get(id) #происхотит поиск в БД выбранного объекта
    api = Api(merchant_id=1396424,
              secret_key='test')#тестовые данные для оплаты
    checkout = Checkout(api=api)
    data = {
        "currency": "RUB",
        "amount": str(item.price) + "00"
    }#создание формы оплыты
    url = checkout.url(data).get('checkout_url')
    return redirect(url)


@app.route('/create', methods=['POST', 'GET'])# метод GET - когда мы переходи на строничку, метод POST - когда мы берем данные с этой
#странички
def create():
    if request.method == "POST":
        title = request.form['title']
        price = request.form['price']

        item = Item(title=title, price=price)

        try:
            db.session.add(item) #создается сессия с БД
            db.session.commit() #добовляется в таблицу item новый объект
            return redirect('/thing') #после завершения перебрасывает на вкладку товары
        except:
            return "Получилась ошибка"
    else:
        return render_template('create.html')




if __name__ == "__main__":
    app.run(debug=True)