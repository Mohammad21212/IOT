# IOT
IOT Project / mapna2

# 1. REST API

## Setup Database
Type this command in your terminal :
```
$ py create_db.py
```

## Explain api code
### Models
First we create User Model & Device Model & Sensor Model & Actuator Model that shows the features of each fields and then we add argument for each one :
#### a. User
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
#### b. Device and Sensor
```
class DeviceModel(db.Model):
    __tablename__ = 'devices'
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
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
sensor_args.add_argument('token', type=str, required=True, help="Token od sensor cannot be blank")

device_args = reqparse.RequestParser()
device_args.add_argument('type', type=str, required=True, help="Type of device cannot be blank")
device_args.add_argument('name', type=str, required=True, help="Name cannot be blank")
device_args.add_argument('value', type=int, required=True, help="Value cannot be blank")
```
#### c. Actuator
```
class ActuatorModel(db.Model): 
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    location = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)

    def __repr__(self): 
        return f"User(token = {self.token}, type = {self.type}, location = {self.location}, status = {self.status})"

actuator_args = reqparse.RequestParser()
actuator_args.add_argument('token', type=str, required=True, help="Token of Actuatr cannot be blank")
actuator_args.add_argument('type', type=str, required=True, help="Type of Actuator cannot be blank")
actuator_args.add_argument('location', type=str, required=True, help="Location cannot be blank")
actuator_args.add_argument('status', type=str, required=True, help="Status cannot be blank")
```

**_NOTE:_**  Important part is that devices are in side of sensor, for example or JSON look like this :
```
{
        'ID' : 'S-0235694',
        'Token' : 'T-197354'
        'Devices' : [
            {
                'type' : 'sensor',
                'name' : 'temp0',
                'value' : 18.5
            },
            {
                'type' : 'act',
                'name' : 'lamp0',
                'value' : 1
            },
            {
                'type' : 'act',
                'name' : 'lamp1',
                'value' : 0
            }
        ]
}
```

### Fields
Then we create fields and show what type they accept :
#### a. User
```
userFields = {
    'id':fields.Integer,
    'username':fields.String,
    'password':fields.String,
    'userrequest':fields.String,
}
```
#### b. Device and Sensor
```
class DeviceSchema(ModelSchema):
    class Meta:
        model = DeviceModel
        sqla_session = db.session

deviceFields = {
    'type': fields.String,
    'name': fields.String,
    'value': fields.Integer,
    'sensor_id': fields.Integer,
}

sensorFields = {
    'id': fields.Integer,
    'token': fields.String,
    'devices': fields.Nested(DeviceSchema, many=True),
}
```
#### c. Actuator
```
actuatorFields = {
    'id': fields.Integer,
    'token': fields.String,
    'type': fields.String,
    'location': fields.String,
    'status': fields.String,
}
```
### Add get, post, patch and delete for Users :
In ```class Users(Resource)``` we create ```def get(self)``` to show all the users with the fields that we described and then in ```def post(self)``` we can add new user :
```
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users 

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], password=args["password"], userrequest=args["userrequest"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201
```
For the second class ```class User(Resource)``` we create ```def get(self, id)``` for get user form there id (like search with id) , in ```def patch(self, id)``` we can update a user by there id , at the end we create ```def delete(self, id)``` that we can delete user by there id :
```
class Users(Resource):
    @marshal_with(userFields)
    def get(self):
        users = UserModel.query.all() 
        return users

    @marshal_with(userFields)
    def post(self):
        args = user_args.parse_args()
        user = UserModel(username=args["username"], password=args["password"], userrequest=args["userrequest"])
        db.session.add(user) 
        db.session.commit()
        users = UserModel.query.all()
        return users, 201

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
```
**_NOTE:_**  We do the same function for devices, device, sensors, sensor, actuators and actuator .






