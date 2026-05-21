from flask import Flask, render_template, redirect, url_for, request, flash
from models import User, House, Purchase
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///realestate.db'

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================= HOME =================

@app.route('/')
def index():
    houses = House.query.limit(6).all()
    return render_template('index.html', houses=houses)

# ================= REGISTER =================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        user = User(username=username, password=password)

        db.session.add(user)
        db.session.commit()

        flash('Registration Successful')
        return redirect(url_for('login'))

    return render_template('register.html')

# ================= LOGIN =================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login Successful')
            return redirect(url_for('index'))

        flash('Invalid Credentials')

    return render_template('login.html')

# ================= LOGOUT =================

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# ================= ADMIN LOGIN =================

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        admin = User.query.filter_by(username=username, is_admin=True).first()

        if admin and check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('add_house'))

        flash('Invalid Admin Credentials')

    return render_template('admin_login.html')

@app.route('/add-house', methods=['GET', 'POST'])
@login_required
def add_house():

    if not current_user.is_admin:
        flash('Only Admin Can Add Houses')
        return redirect(url_for('index'))

    if request.method == 'POST':

        title = request.form['title']
        city = request.form['city']
        price = request.form['price']
        image = request.form['image']

        house = House(
            title=title,
            city=city,
            price=price,
            image=image
        )

        db.session.add(house)
        db.session.commit()

        flash('House Added Successfully')

    return render_template('add_house.html')


# ================= EDIT HOUSE =================

@app.route('/edit-house/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_house(id):

    if not current_user.is_admin:
        flash('Only Admin Can Edit Houses')
        return redirect(url_for('index'))

    house = House.query.get_or_404(id)

    if request.method == 'POST':

        house.title = request.form['title']
        house.city = request.form['city']
        house.price = request.form['price']
        house.image = request.form['image']

        db.session.commit()

        flash('House Updated Successfully')

        return redirect(url_for('houses'))

    return render_template('edit_house.html', house=houses)


# ================= DELETE HOUSE =================

@app.route('/delete-house/<int:id>', methods=['POST'])
@login_required
def delete_house(id):

    if not current_user.is_admin:
        flash('Only Admin Can Delete Houses')
        return redirect(url_for('index'))

    house = House.query.get_or_404(id)

    db.session.delete(house)
    db.session.commit()

    flash('House Deleted Successfully')

    return redirect(url_for('houses'))

# ================= ALL HOUSES =================

@app.route('/houses')
def houses():

    city = request.args.get('city')
    min_price = request.args.get('min_price')
    max_price = request.args.get('max_price')

    query = House.query

    if city:
        query = query.filter(House.city.ilike(f"%{city}%"))

    if min_price:
        query = query.filter(House.price >= int(min_price))

    if max_price:
        query = query.filter(House.price <= int(max_price))

    houses = query.all()

    return render_template('houses.html', houses=houses)



@app.route('/buy-house/<int:id>', methods=['GET', 'POST'])
@login_required
def buy_house(id):

    house = House.query.get_or_404(id)

    if request.method == 'POST':

        buyer_name = request.form['buyer_name']
        phone = request.form['phone']

        purchase = Purchase(
            user_id=current_user.id,
            house_id=house.id,
            buyer_name=buyer_name,
            phone=phone
        )

        db.session.add(purchase)
        db.session.commit()

        flash('Purchase Request Sent')

        return redirect(url_for('houses'))

    return render_template('buy_house.html', house=house)



@app.route('/user-edit-house/<int:id>', methods=['GET', 'POST'])
@login_required
def user_edit_house(id):

    house = House.query.get_or_404(id)

    if request.method == 'POST':

        house.title = request.form['title']
        house.city = request.form['city']
        house.price = request.form['price']
        house.image = request.form['image']

        db.session.commit()

        flash('House Updated Successfully')

        return redirect(url_for('houses'))

    return render_template('user_edit_house.html', house=house)


@app.route('/user-delete-house/<int:id>', methods=['POST'])
@login_required
def user_delete_house(id):

    house = House.query.get_or_404(id)

    db.session.delete(house)
    db.session.commit()

    flash('House Deleted Successfully')

    return redirect(url_for('houses'))
 
@app.route('/purchase-requests')
@login_required
def purchase_requests():

    if not current_user.is_admin:
        flash('Access Denied')
        return redirect(url_for('index'))

    purchases = Purchase.query.all()

    return render_template(
        'purchase_requests.html',
        purchases=purchases
    )   

# ================= CREATE ADMIN =================

@app.route('/create-admin')
def create_admin():

    admin_exist = User.query.filter_by(username='admin').first()

    if admin_exist:
        return "Admin Already Exists"

    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()

    return "Admin Created"

# ================= RUN =================

if __name__ == '__main__':

    with app.app_context():
        db.create_all()

    app.run(debug=True)