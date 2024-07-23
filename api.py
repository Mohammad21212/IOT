from flask import Flask 
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Resource, Api, reqparse, fields, marshal_with, abort
from marshmallow_sqlalchemy import ModelSchema

# -----<<Database>>-----
app = Flask(__name__) 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app) 
api = Api(app)

# -----<<Models>>-----
# <<User>>
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

# <<Gateway and Device>>

class DeviceModel(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer,unique=True , nullable=False)
    token = db.Column(db.String(80), unique=True, nullable=False)
    type = db.Column(db.String(80), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    value = db.Column(db.Integer, nullable=False)
    datatype = db.Column(db.String, nullable=False)    

    def __repr__(self):
        return f"Device(token={self.token}, type={self.type}, name={self.name}, value={self.value}, datatype={self.datatype})"

class GatewayModel(db.Model): 
    __tablename__ = 'Gateways'
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(80), unique=True, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    devices = db.relationship('DeviceModel', backref='gateway', lazy=True)

    def __repr__(self): 
        return f"Sensor(id = {self.id}, token = {self.token}, name={self.name}, devices={self.devices})"
    
    
class DeviceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceModel
        include_fk = True

class GatewaySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = GatewayModel
        include_relationships = True
        load_instance = True

    devices = fields.List(fields.Nested(DeviceSchema))

gateway_parser = reqparse.RequestParser()
gateway_parser.add_argument('token', type=str, required=True, help='Token is required')
gateway_parser.add_argument('name', type=str, required=True, help='Name is required')

device_parser = reqparse.RequestParser()
device_parser.add_argument('token', type=str, required=True, help='Device Token is required')
device_parser.add_argument('type', type=str, required=True, help='Device type is required')
device_parser.add_argument('name', type=str, required=True, help='Device name is required')
device_parser.add_argument('value', type=float, required=True, help='Device value is required')
device_parser.add_argument('datatype', type=float, required=True, help='DataType is required')

# -----<<Fields>>-----
# <<User>>
userFields = {
    'id':fields.Integer,
    'username':fields.String,
    'password':fields.String,
    'userrequest':fields.String,
}

# <<Gateway and Device>>

deviceFields = {
    'id': fields.Integer,
    'token': fields.String, 
    'type': fields.String,
    'name': fields.String,
    'value': fields.Integer,
    'datatype': fields.Integer,
}

gatewayFields = {
    'id': fields.Integer,
    'token': fields.String,
    'name': fields.String,
    'devices': fields.List(fields.Nested(deviceFields))
}

# -----<<get, post, patch and delete>>-----
# <<User>>
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

# <<Gateway and Device>>

class Gateways(Resource):
    @marshal_with(gatewayFields)
    def get(self, id):
        gateway = GatewayModel.query.get_or_404(id)
        gateway_schema = GatewaySchema()
        return gateway_schema.dump(gateway), 200
    
    @marshal_with(gatewayFields)
    def post(self):
        args = gateway_parser.parse_args()
        devices = ('devices', [])
        gateway = GatewayModel(token=args['token'], name=args['name'])
       
        for device_data in devices:
            device_args = device_parser.parse_args(strict=True)
            device = DeviceModel(**device_args)
            gateway.devices.append(device)
       
        db.session.add(gateway)
        db.session.commit()
       
        Gateway_Schema = GatewaySchema()
        return Gateway_Schema.dump(gateway), 201
    
    @marshal_with(gatewayFields)
    def patch(self, id):
        gateway = GatewayModel.query.get_or_404(id)
        args = gateway_parser.parse_args()
        devices = ('devices', [])
       
        gateway.token = args['token']
       
        # Remove existing devices
        DeviceModel.query.filter_by(id).delete()
       
        for device_data in devices:
            device_args = device_parser.parse_args(strict=True)
            device = DeviceModel(**device_args)
            gateway.devices.append(device)
       
        db.session.commit()
       
        gateway_schema = GatewaySchema()
        return gateway_schema.dump(gateway), 200

api.add_resource(Users, '/api/users/')
api.add_resource(User, '/api/users/<int:id>')
api.add_resource(Gateways, '/api/gateways/<int:id>')

@app.route('/')
def home():
    return '<h1>REST API</h1>'

if __name__ == '__main__':
    app.run(debug=True) 
