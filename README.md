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
$ class UserModel(db.Model): 
$     id = db.Column(db.Integer, primary_key=True)
$     username = db.Column(db.String(80), unique=True, nullable=False)
$     password = db.Column(db.String(80), nullable=False)
$     userrequest = db.Column(db.String(80), nullable=False)
$ 
$     def __repr__(self): 
$         return f"User(username = {self.username}, password = {self.password}, userrequest = {self.userrequest})"
$ 
$ user_args = reqparse.RequestParser()
$ user_args.add_argument('username', type=str, required=True, help="Username cannot be blank")
$ user_args.add_argument('password', type=str, required=True, help="Password cannot be blank")
$ user_args.add_argument('userrequest', type=str, required=True, help="Userrequest cannot be blank")
```
