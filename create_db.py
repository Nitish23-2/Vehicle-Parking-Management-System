from app import create_app,db
from app.models import ParkingLot, ParkingSpot

app= create_app()

with app.app_context():
    db.create_all()
    if not ParkingLot.query.first():
        lot1= ParkingLot(name= "Lot A", location_name= "North Campus", address= "Main Road, North Campus", pincode= "123456", price_per_hour= 20.0, max_spots= 10)
        lot2= ParkingLot(name= "Lot B", location_name= "South Gate", address="South Avenue, Near Library", pincode="654321", price_per_hour=30.0, max_spots= 8)

        db.session.add_all([lot1, lot2])
        db.session.commit()

        for lot in [lot1, lot2]:
            for _ in range(lot.max_spots):
                spot= ParkingSpot(lot_id= lot.id, status="A")
                db.session.add(spot)

        db.session.commit()
        print("Database Created and populated with lots & spots")  
    else:
        print('Database already contain Parking Lots')
    

