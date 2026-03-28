from flask import Blueprint, render_template, redirect,url_for, flash, request, after_this_request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import ParkingLot, ParkingSpot, Reservation, User
from datetime import datetime
from zoneinfo import ZoneInfo

from . import db, login_manager
from .models import User
from .forms import RegisterForm, LoginForm

main=Blueprint('main', __name__)
IST= ZoneInfo('Asia/Kolkata')

#--------------User Loader--------------------

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#-----------------Home------------------------

@main.route('/')
def home():
    return render_template('home.html')


#----------------User Register----------------

@main.route('/register', methods=['GET','POST'])
def register():
    form= RegisterForm()
    if form.validate_on_submit():
        existing_user= User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.', 'danger')
            return redirect(url_for('main.register'))
        

        hashed_password= generate_password_hash(form.password.data)
        new_user= User(full_name=form.full_name.data, email=form.email.data, password=hashed_password )
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful. Please login.', 'Success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)



#----------------------------------------User Login-------------------------------------------------

@main.route('/login', methods=['GET','POST'])
def login():
    form= LoginForm()
    if form.validate_on_submit():
        user= User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('main.user_dashboard'))
        else:
            flash('Invalid Credentials.', 'danger')
    return render_template('login.html', form=form)


#-----------------------------Admin Login-----------------------------------------

from flask import session
@main.route('/admin-login', methods=['GET','POST'])
def admin_login():
    if request.method=='POST':
        email= request.form.get('email')
        password= request.form.get('password')
        if email == '24f2001383@ds.study.iitm.ac.in' and password=='admin123':
            session.permamnent=True
            session['admin_logged_in']=True
            return redirect(url_for('main.admin_dashboard'))
        else:
            flash("Invalid Admin Credentials.", 'danger')
    return render_template('admin_login.html')



#-------------------------------User Dashboard------------------------------

@main.route('/user/dashboard')
@login_required
def user_dashboard():
    lots= ParkingLot.query.all()
    active_reservation= Reservation.query.filter_by(user_id= current_user.id, end_time= None).first()

    if active_reservation:
        reserved_spot= ParkingSpot.query.get(active_reservation.spot_id)
        reserved_lot= ParkingLot.query.get(reserved_spot.lot_id)
        
        spot_status= {reserved_spot.id: active_reservation}
        selected_lot= reserved_lot
        selected_lot.spots=[reserved_spot]
    
        return render_template('user_dashboard.html', lots=lots, selected_lot= reserved_lot, reserved_only= True, spot_status=spot_status, user= current_user)
    
    lot_id= request.args.get('lot_id', type= int)
    selected_lot= ParkingLot.query.get(lot_id) if lot_id else None

    spot_status= {}
    if selected_lot:
        for spot in selected_lot.spots:
            active_res= next((res for res in spot.reservations if res.end_time is None),None)
            spot_status[spot.id]= active_res
    return render_template('user_dashboard.html', lots=lots, selected_lot=selected_lot, user=current_user, spot_status=spot_status)


#-----------------------------Admin Dashboard--------------------------------
@main.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        flash("Unauthorized Access,",'danger')
        return redirect(url_for('main.admin_login'))
    
    lots= ParkingLot.query.all()
    lot_data= []

    for lot in lots:
        total_spots= int(len(lot.spots))
        available= sum(1 for spot in lot.spots if spot.status=="A")
        occupied= total_spots - available

        lot_data.append({'id':lot.id, 'name':lot.name, 'location':lot.location_name, 'price':lot.price_per_hour, 'total_spots':total_spots, 'available':available, 'occupied':occupied})


    return render_template('admin_dashboard.html', lots=lot_data)


#---------------------User Logout-------------------------
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out Successfully.', 'info')
    return redirect(url_for('main.login'))


#--------------------Admin Logout-------------------------

@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in',None)
    flash('Admin Logged Out.','info')
    return redirect(url_for('main.admin_login'))    

#-----------------------Cache Manage------------------------

@main.after_app_request
def add_no_cache_headers(response):
    response.headers['Cache-Control']= "no-store, no-cache, must-revalidate, post-check=0, precheck=0, max-age=0"
    response.headers["Pragma"]= 'no-cache'
    response.headers["Expires"]= "-1"
    return response


#-------------------------------------------Reserve Spot--------------------------------------------

@main.route('/reserve/<int:spot_id>', methods=['POST'])
@login_required
def reserve_spot(spot_id):
    spot= ParkingSpot.query.get_or_404(spot_id)


    if spot.status=="O":
        flash('Spot Already Occupied!','danger')
        return redirect(url_for('main.user_dashboard'))
    
    existing= Reservation.query.filter_by(user_id=current_user.id, end_time=None).first()
    if existing:
        flash('You already have a Reservation.','Warning')
        return redirect(url_for('main.user_dashboard'))
    

    spot.status="O"
    vehicle_number= request.form.get('vehicle_number')
    reservation= Reservation(user_id= current_user.id, spot_id= spot.id, vehicle_number=vehicle_number)
    db.session.add(reservation)
    db.session.commit()

    flash('Spot reserved successfully!','Success')
    return redirect(url_for('main.user_dashboard'))


#-------------------------------------------Auto Reserve--------------------------------------------

@main.route('/auto-reserve/', methods=["POST"])
@login_required
def auto_reserve():
    lot_id= request.form.get('lot_id', type=int)
    lot= ParkingLot.query.get_or_404(lot_id)

    existing= Reservation.query.filter_by(user_id= current_user.id, end_time=None).first() 
    if existing:
        flash('You Already Have a Reservation.','danger')
        return redirect(url_for('main.user_dashboard', lot_id=lot_id)) 

    for spot in lot.spots:
        active= Reservation.query.filter_by(spot_id=spot.id, end_time=None).first()
        if not active:
            vehicle_number= request.form.get('vehicle_number')
            reservation= Reservation(user_id= current_user.id, spot_id=spot.id, vehicle_number=vehicle_number)
            spot.status="O"
            db.session.add(reservation)
            db.session.commit()
            flash(f'Spot {spot.id} in {lot.name} reserved successfully!','Success')
            return redirect(url_for('main.user_dashboard', lot_id=lot_id))

    flash('No available spots in this Lot','danger')
    return redirect(url_for('main.user_dashboard', lot_id=lot_id))

    



#-------------------------------------------Release Spot--------------------------------------------

@main.route('/release/<int:spot_id>', methods=['POST'])
@login_required
def release_spot(spot_id):
    spot= ParkingSpot.query.get_or_404(spot_id)
    reservation= Reservation.query.filter_by(spot_id= spot.id, user_id= current_user.id, end_time=None).first()

    if reservation:
        reservation.end_time = datetime.now(IST)
        if reservation.start_time.tzinfo is None:
            reservation.start_time= reservation.start_time.replace(tzinfo= IST)
        duration = (reservation.end_time - reservation.start_time).seconds / 3600  # in hours
        reservation.cost = round(duration * spot.lot.price_per_hour, 2)
        spot.status = "A"
        db.session.commit()
        flash(f'Spot released. Total cost: ₹{reservation.cost}', 'success')
    else:
        flash("You cannot release any spot.",'danger')

    return redirect(url_for('main.user_dashboard'))   


#-----------------------------User History--------------------------------------

@main.route("/user/history")
@login_required
def parking_history():
    history= Reservation.query.filter_by(user_id= current_user.id).filter(Reservation.end_time.isnot(None)).order_by(Reservation.start_time.desc()).all()
    return render_template('parking_history.html', history=history, user=current_user)


#----------------------------Creating Lot----------------------------------------

@main.route('/admin/create-lot', methods=["GET","POST"])
def create_lot():
    if not session.get('admin_logged_in'):
        flash('Unauthorized access','danger')
        return redirect(url_for('main.admin_login'))
    
    if request.method== "POST" :
        name= request.form.get('name')
        location_name= request.form.get('location_name')
        address= request.form.get('address')
        pincode= request.form.get('pincode')
        price_per_hour= request.form.get('price_per_hour')
        max_spots= int(request.form.get('max_spots'))

        new_lot= ParkingLot(name= name, location_name= location_name, address= address, pincode= pincode, price_per_hour= float(price_per_hour), max_spots=max_spots)

        db.session.add(new_lot)
        db.session.commit()
        
        for _ in range(max_spots):
            spot= ParkingSpot(lot_id= new_lot.id, status="A")
            db.session.add(spot)

        db.session.commit()
        flash('Parking lot created successfully.','Success')
        return redirect(url_for('main.admin_dashboard'))
    

    return render_template('create_lot.html')

#----------------------------------Spot View for Admin----------------------------------------

@main.route('/admin/lot/<int:lot_id>/spots')
def view_spots(lot_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    lot= ParkingLot.query.get_or_404(lot_id)
    spots= lot.spots

    return render_template('view_spots.html', spots=spots, lot=lot)

#------------------------------Edit Lot----------------------------------

@main.route('/admin/lot/<int:lot_id>/edit', methods=["GET","POST"])
def edit_lot(lot_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    lot= ParkingLot.query.get_or_404(lot_id)

    if request.method=="POST":
        lot.name= request.form['name']
        lot.location_name= request.form['location_name']
        lot.address= request.form['address']
        lot.pincode= request.form['pincode']
        lot.price_per_hour= float(request.form['price_per_hour'])
        db.session.commit()

        flash('Lot Updated Successfully.','Success')
        return redirect(url_for('main.admin_dashboard'))
    
    return render_template('edit_lot.html', lot=lot)


#-------------------------------------Delete Lot---------------------------------

@main.route('/admin/lot/<int:lot_id>/delete', methods=["POST"])
def delete_lot(lot_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    lot= ParkingLot.query.get_or_404(lot_id)

    for spot in lot.spots:
        Reservation.query.filter_by(spot_id= spot.id).delete()
        db.session.delete(spot)

    db.session.delete(lot)
    db.session.commit()

    flash('Lot and associated spots Deleted Successfully.','Success')
    return redirect(url_for('main.admin_dashboard'))

#-------------------------Spot Delete-------------------------------

@main.route('/admin/spot/<int:spot_id>/delete', methods=["POST"])
def delete_spot(spot_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    spot= ParkingSpot.query.get_or_404(spot_id)

    lot_id= spot.lot_id

    active_res= Reservation.query.filter_by(spot_id= spot.id, end_time= None).first()
    if active_res:
        flash("This spot can't be deleted as it's currently occupied","warning")
        return redirect(url_for('main.view_spots',lot_id=lot_id))

    Reservation.query.filter_by(spot_id=spot.id).delete()

    db.session.delete(spot)
    db.session.commit()

    flash(f'Spot ID {spot.id} deleted successfully.','success')
    return redirect(url_for('main.view_spots', lot_id=lot_id))


#--------------------------All User View for Admin------------------------------------------

@main.route('/admin/users')
def view_all_users():
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))

    users= User.query.all()
    user_data= []

    for user in users:
        active_res= Reservation.query.filter_by(user_id= user.id, end_time=None).first()
        current_spot= f"Spot {active_res.spot.id} (Lot: {active_res.spot.lot.name})" if active_res else "None"

        user_data.append({'id': user.id, 'name':user.full_name, 'email':user.email, 'currents_spot': current_spot})

    return render_template('admin_all_users.html', users=user_data)

#----------------------------------------Specific User Hiostory------------------------------------------------------

@main.route('/admin/user/<int:user_id>/history')
def admin_user_history(user_id):
    if not session.get('admin_logged_in'):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    user= User.query.get_or_404(user_id)
    history= Reservation.query.filter_by(user_id= user_id).order_by(Reservation.start_time.desc()).all()

    return render_template('admin_user_history.html', user=user, history=history)

#-------------------------------------Spot Wise History-------------------------------------------------

@main.route('/admin/spot/<int:spot_id>/history')
def spot_history(spot_id):
    if not session.get("admin_logged_in"):
        flash('Unauthorized Access.','danger')
        return redirect(url_for('main.admin_login'))
    
    spot= ParkingSpot.query.get_or_404(spot_id)
    lot= ParkingLot.query.get(spot.lot_id)
    history= Reservation.query.filter_by(spot_id=spot_id).order_by(Reservation.start_time.desc()).all()

    return render_template('spot_history.html', spot=spot, lot=lot, history=history)

#-------------------------------------------Admin Search Feature---------------------------------------------

@main.route('/admin/search')
def admin_search():
    if not session.get("admin_logged_in"):
        flash('Unauthorized access.','danger')
        return redirect(url_for('main.admin_login'))
    
    query= request.args.get('query','').strip().lower()

    lots= ParkingLot.query.filter( (ParkingLot.name.like(f"%{query}%")) | (ParkingLot.location_name.like(f"%{query}%")) | (ParkingLot.pincode.ilike(f"%{query}%")) ).all()
    
    for lot in lots:
        lot.available= ParkingSpot.query.filter_by(lot_id=lot.id, status="A").count()
        lot.occupied= ParkingSpot.query.filter_by(lot_id=lot.id, status="O").count()

    reservations=[] 
    if query.isdigit():
        query_int= int(query)
        reservations= Reservation.query.filter( (Reservation.spot_id==query_int) | (Reservation.user_id==query_int) ).all()

    return render_template('admin_search_result.html', lots=lots, query=query, reservations=reservations) 