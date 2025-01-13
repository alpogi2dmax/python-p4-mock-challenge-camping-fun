#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route('/')
def home():
    return ''

class Campers(Resource):

    def get(self):
        campers = [camper.to_dict(only=('id', 'name', 'age')) for camper in Camper.query.all()]
        return make_response(campers, 200)
    
    def post(self):
        try:
            data = request.get_json()
            new_camper = Camper(
                name = data['name'],
                age = data['age']
            )
            db.session.add(new_camper)
            db.session.commit()
            response_body = new_camper.to_dict()
            return make_response(response_body, 201)
        except:
            response_body = {"errors":"errors"}
            return make_response(response_body, 400)

    
api.add_resource(Campers, '/campers')

class CampersByID(Resource):

    def get(self, id):
        camper = Camper.query.filter_by(id=id).first()
        if camper:
            camper_dict = camper.to_dict()
            return make_response(camper_dict, 200)
        else:
            return make_response({'error': 'Camper not found'}, 404)
        
    def patch(self, id):
        try:
            camper = Camper.query.filter_by(id=id).first()
            data = request.get_json()

            if not data.get('name'):
                raise ValueError("Name cannot be empty")
            
            if data.get('age') < 8 or data.get('age') > 18:
                raise ValueError("Age must be between 8 and 18")

            if camper:
                for attr, value in data.items():
                    setattr(camper, attr, value)

                db.session.add(camper)
                db.session.commit()

                response_dict = camper.to_dict()

                return make_response(response_dict, 202)
            
            else:

                return make_response({"error": "Camper not found"}, 404)
            
        except ValueError as ve:
            response_body = {"errors": ["validation errors"]}
            return make_response(response_body, 400)

        except Exception as e:
            response_body = {"errors": ["An unexpected error occurred"]}
            return make_response(response_body, 400)
    
api.add_resource(CampersByID, '/campers/<int:id>')

class Activities(Resource):
   
    def get(self):

        activities = [activity.to_dict() for activity in Activity.query.all()]
        return make_response(activities, 200)

api.add_resource(Activities, '/activities')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

class ActivitiesByID(Resource):

    def delete(self, id):

        activity = Activity.query.filter_by(id=id).first()

        if activity:
            db.session.delete(activity)
            db.session.commit()

            response_dict = ""

            return make_response(response_dict, 204)
        else:
            return make_response({"error": "Activity not found"}, 404)

api.add_resource(ActivitiesByID, '/activities/<int:id>')

class Signups(Resource):

    def post(self):

        try:
            data = request.get_json()

            new_signup = Signup(
                activity_id = data['activity_id'],
                camper_id = data['camper_id'],
                time = data['time'],
            )

            db.session.add(new_signup)
            db.session.commit()

            response_body = new_signup.to_dict()
            return make_response(response_body, 201)
        except:
            response_body = {"errors": ["validation errors"]}
            return make_response(response_body, 400)

api.add_resource(Signups, '/signups')