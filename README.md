# IOT
IOT Project / mapna2

# 1. REST API

## Setup for database
Type this command in your terminal :
```
$ py create_db.py
```

## Explain api code
### Models
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
**_NOTE:_**  Important part is that devices are in side of sensor, for example or JSON look like this :
```
{
        'ID' : 'blablabla',
        'Token' : 'blablabla'
        'Devices' : [
            {
                'type' : 'sensor',
                'name' : 'temp0',
                'value' : '18.5'
            },
            {
                'type' : 'act',
                'name' : 'lamp0',
                'value' : '1'
            },
            {
                'type' : 'act',
                'name' : 'lamp1',
                'value' : '0'
            }
        ]
}
```

### Fields
Then we create fields and show what type they accept :
```
userFields = {
    'id':fields.Integer,
    'username':fields.String,
    'password':fields.String,
    'userrequest':fields.String,
}

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
**_NOTE:_**  We do the same function for devices, device, sensors and sensor .






