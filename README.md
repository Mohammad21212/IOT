# IOT
IOT Project / mapna2

# 1. REST API

## Setup for database
Type this command in your terminal :
```
$ py create_db.py
```

## Explain api code
First we create User Model & Device Model & Sensor Model that shows the features of each fields and then we add argument for each one :
```
class UserModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    userrequest = db.Column(db.String(80), nullable=False)

    def __repr__(self): 
        return f"User(username = {self.username}, password = {self.password}, userrequest = {self.userrequest})"

user_args = reqparse.RequestParser()
user_args.add_argument('username', type=str, required=True, help="Username cannot be blank")
user_args.add_argument('password', type=str, required=True, help="Password cannot be blank")
user_args.add_argument('userrequest', type=str, required=True, help="Userrequest cannot be blank")
```
```
class DeviceModel(db.Model):
    __tablename__ = 'devices'
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.String(80), nullable=False)
    sensor_id = db.Column(db.Integer, db.ForeignKey('sensors.id'), nullable=False)
    sensor = db.relationship('SensorModel', backref=db.backref('devices', lazy=True))

    def __repr__(self):
        return f"Device(type={self.type}, name={self.name}, value={self.value})"

class SensorModel(db.Model): 
    __tablename__ = 'sensors'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    devices = db.relationship('DeviceModel', backref='sensor', lazy=True)

    def __repr__(self): 
        return f"Sensor(id = {self.id}, token = {self.token}, devices={self.devices})"

sensor_args = reqparse.RequestParser()
sensor_args.add_argument('token', type=str, required=True, help="Token cannot be blank")

device_args = reqparse.RequestParser()
device_args.add_argument('type', type=str, required=True, help="Type cannot be blank")
device_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
device_args.add_argument('value', type=str, required=True, help="Value cannot be blank")
```
