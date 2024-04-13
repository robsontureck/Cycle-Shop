from flask import Blueprint, render_template, request, url_for, session, flash, redirect
from .models import Brand, Bicycle, Images, Order, OrderDetails
from datetime import datetime
from .forms import CheckoutForm
from . import db
import sys

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Route for customer landing page"""
    bikes = Bicycle.query.all()
    brands = Brand.query.all()
    return render_template('index.html', bikes=bikes, brands=brands)


@bp.route('/search_results/')
@bp.route('/search_results/<filter>/')
@bp.route('/search_results/<filter>/<search>/')
def search(filter=None, search=None):
    """Route for displaying search results page. Takes variable for 'filter'
    to filter search results before displaying. Takes 'search' variable to filter by search
    result if user is not coming from the index page. """
    # get search term from search bar if not applying a filter
    if not search:
        search = request.args.get('search')
        search = F"%{search}%"
    #search bicycles and brands for search query
    bicycles = Bicycle.query.filter(Bicycle.model.like(search)).all()
    brands = Brand.query.filter(Brand.name.like(search)).all()
    # add bikes from brands to bicycles list
    brand_list = []
    for brand in brands:
        brand_list = brand_list + \
            brand.bicycles
    for i in brand_list:
        if i not in bicycles:
            bicycles.append(i)
    # filter search results if applicable
    filtered_bikes = []
    if filter:
        filter = filter.split('.')
        # filter by brand if filter passed through is Brand
        if filter[0] == 'brand':
            for bike in bicycles:
                if bike.brand_id == int(filter[1]):
                    filtered_bikes.append(bike)
        # filter by price
        elif filter[0] == 'price':
            try:
                price_from = request.args.get('price_from', type=float)
                price_to = request.args.get('price_to', type=float)
                if price_from is None:
                    price_from = 0
                if price_to is None:
                    price_to = 999999999999999
                for bike in bicycles:
                    if (price_from < bike.price < price_to):
                        filtered_bikes.append(bike)
            except ValueError:
                filtered_bikes = bicycles
    else:
        filtered_bikes = bicycles
    # build list of brands in search results to populate search results side bar
    return_brands = []
    for bike in filtered_bikes:
        b = bike.Brand
        found = False
        for i in return_brands:
            if i[0] == b:
                i[1] += 1
                found = True
                break
        if not found:
            return_brands.append([b, 1])
    return render_template('search_results.html', search_results=filtered_bikes, return_brands=return_brands, search_term=search)


@bp.route('/bicycles/<int:bicycle_id>/')
def bicycle_detail(bicycle_id):
    """Route for bicycle item detail page. Takes bicycle_id and displays bike ino."""
    bike = Bicycle.query.get(bicycle_id)
    images = Images.query.filter(Images.bicycle_id == bicycle_id).all()
    brand = Brand.query.get(bike.brand_id)
    return render_template('item.html', images=images, brand=brand, bike=bike)


@bp.route('/order', methods=['POST', 'GET'])
def order():
    print(request.form)
    quantity = request.form.get('quantityInput', type=int)
    if quantity is None:
        quantity = 1
    print(type(quantity))
    bike_id = request.values.get('bike_id')
    # retrieve order if there is one
    if 'order_id' in session.keys():
        order = Order.query.get(session['order_id'])
        # order will be None if order_id stale
    else:
        # there is no order
        order = None

    # create new order if needed
    if order is None:
        order = Order(status=False, firstname='', surname='',
                      email='', phone='', totalcost=0, date=datetime.now())
        try:
            db.session.add(order)
            db.session.commit()
            session['order_id'] = order.id
        except:
            print('failed at creating a new order')
            order = None

    # calcultate totalprice
    totalprice = 0

    if order is not None:
        for item in order.orderdetails:
            totalprice += Bicycle.query.get(item.bicycle_id).price * \
                item.quantity

    # are we adding an item?
    if bike_id is not None and order is not None:
        bicycle = Bicycle.query.get(bike_id)
        order_item = OrderDetails(
            order_id=order.id, bicycle_id=bike_id, quantity=quantity)
        if not (bicycle in order.bicycles):
            try:
                db.session.add(order_item)
                db.session.commit()
            except Exception as e:
                print(e)
                return 'There was an issue adding the item to your basket'
            return redirect(url_for('main.order'))
        else:
            # increment quantity in orderdetails by one
            order_bike = OrderDetails.query.get((order.id, bike_id))
            order_bike.quantity += quantity
            db.session.commit()
            return redirect(url_for('main.order'))
    # create list of quantities to give to html page
    quantities = []
    for bike in order.bicycles:
        order_bike = OrderDetails.query.get((order.id, bike.id))
        quantities.append(order_bike.quantity)
    return render_template('order.html', order=order, totalprice=totalprice, quantities=quantities)


@bp.route('/deleteorderitem', methods=['POST'])
def deleteorderitem():
    id = request.form['id']
    if 'order_id' in session:
        order = Order.query.get_or_404(session['order_id'])
        try:
            bike_to_delete = OrderDetails.query.get((order.id, id))
            db.session.delete(bike_to_delete)
            db.session.commit()
            return redirect(url_for('main.order'))
        except Exception as e:
            print(e)
            return 'Problem deleting item from order'
    return redirect(url_for('main.order'))


@bp.route('/deleteorder')
def deleteorder():
    if 'order_id' in session:
        del session['order_id']
        flash('All items deleted')
    return redirect(url_for('main.index'))


@bp.route('/checkout', methods=['POST', 'GET'])
def checkout():
    form = CheckoutForm()
    if 'order_id' in session:
        order = Order.query.get_or_404(session['order_id'])

        if form.validate_on_submit():
            order.status = True
            order.firstname = form.firstname.data
            order.surname = form.surname.data
            order.email = form.email.data
            order.phone = form.phone.data
            totalcost = 0
            for item in order.orderdetails:
                totalcost += Bicycle.query.get(
                    item.bicycle_id).price * item.quantity
            order.totalcost = totalcost
            try:
                db.session.commit()
                del session['order_id']
                flash(
                    'Thank you for shopping with us!')
                return redirect(url_for('main.index'))
            except:
                return 'There was an issue completing your order'
    return render_template('checkout.html', form=form)
