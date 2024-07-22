from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from marshmallow_sqlalchemy import ModelSchema

app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app) 
api = Api(app)

# User
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

userFields = {
    'id':fields.Integer,
    'username':fields.String,
    'password':fields.String,
    'userrequest':fields.String,
}

class Users(Resource):
    # get for users
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users 
    # post for users
    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], password=args["password"], userrequest=args["userrequest"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

# just for one user
class User(Resource):
    @marshal_with(userFields)
    def get(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        return user 
    
    @marshal_with(userFields)
    def patch(self, id):
        args = user_args.parse_args()
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        user.username = args["username"]
        user.password = args["password"]
        user.userrequest = args["userrequest"]
        db.session.commit()
        return user 
    
    @marshal_with(userFields)
    def delete(self, id):
        user = UserModel.query.filter_by(id=id).first() 
        if not user: 
            abort(404, message="User not found")
        db.session.delete(user)
        db.session.commit()
        users = UserModel.query.all()
        return users
    
############################################################

# Sensor and Device
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

class DeviceSchema(ModelSchema):
    class Meta:
        model = DeviceModel
        sqla_session = db.session

deviceFields = {
    'type': fields.String,
    'name': fields.String,
    'value': fields.String,
    'sensor_id': fields.Integer,
}

sensorFields = {
    'id': fields.Integer,
    'token': fields.String,
    'devices': fields.Nested(DeviceSchema, many=True),
}

class Devices(Resource):
    # get for devices
    @marshal_with(deviceFields)
    def get(self):
        devices = DeviceModel.query.all()
        return devices

    # post for devices
    @marshal_with(deviceFields)
    def post(self):
        args = device_args.parse_args()
        device = DeviceModel(type=args["type"], name=args["name"], value=args["value"], sensor_id=args["sensor_id"])
        db.session.add(device)
        db.session.commit()
        devices = DeviceModel.query.all()
        return devices, 201
    
class Device(Resource):
    @marshal_with(deviceFields)
    def get(self, id):
        device = UserModel.query.filter_by(id=id).first() 
        if not device: 
            abort(404)
        return device 
    
    @marshal_with(deviceFields)
    def patch(self, id):
        device = DeviceModel.query.get(id)
        if device is None:
            abort(404)
        args = device_args.parse_args()
        device.type = args["type"]
        device.name = args["name"]
        device.value = args["value"]
        device.sensor_id = args["sensor_id"]
        db.session.commit()
        return device, 200
    
    def delete(self, id):
        device = DeviceModel.query.get(id)
        if device is None:
            abort(404)
        db.session.delete(device)
        db.session.commit()
        return "", 204


class Sensors(Resource):
    # get for sensors
    @marshal_with(sensorFields)
    def get(self):
        sensors = SensorModel.query.all()
        return sensors

    # post for sensors
    @marshal_with(sensorFields)
    def post(self):
        args = sensor_args.parse_args()
        sensor = SensorModel(token=args["token"])
        db.session.add(sensor)
        db.session.commit()
        sensors = SensorModel.query.all()
        return sensors, 201
    
class Sensor(Resource):
    @marshal_with(deviceFields)
    def get(self, id):
        sensor = UserModel.query.filter_by(id=id).first() 
        if not sensor: 
            abort(404)
        return sensor
    
    @marshal_with(sensorFields)
    def patch(self, id):
        sensor = SensorModel.query.get(id)
        if sensor is None:
            abort(404)
        args = sensor_args.parse_args()
        sensor.token = args["token"]
        db.session.commit()
        return sensor, 200
    
    # delete for sensors
    def delete(self, id):
        sensor = SensorModel.query.get(id)
        if sensor is None:
            abort(404)
        db.session.delete(sensor)
        db.session.commit()
        return "", 204

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')

api.add_resource(Devices, '/api/devices/')
api.add_resource(Device, '/api/devices/<int:id>')

api.add_resource(Sensors, '/api/sensors/')
api.add_resource(Sensor, '/api/sensors/<int:id>')


@app.route('/')
def home():
    return '<h1>REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True) 