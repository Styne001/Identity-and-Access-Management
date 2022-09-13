import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
# Function to get drink title and reciepe[color and parts] from the database
def get_drinks():
    try:
        # Query the database to get drinks
        drinks = Drink.query.all()
        # formatting to details of drinks with their ids, title and short reciepe
        formatted_drinks = [drink.short() for drink in drinks]
        #return success and formatted drinks
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except Exception:
        abort(422)

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
# requires permission get:drinks-detail
@requires_auth('get:drinks-details')
# Function to get drink title and reciepe[color, ingredients and parts] from the database
def get_drinks_detail(payload):
    try:
        # Query the database to get all drinks
        drinks = Drink.query.all()
        # formatting to get details of drinks with their ids, title and reciepe
        formatted_drinks = [drink.long() for drink in drinks]
        # return success and formatted drinks
        return jsonify({
            'success': True,
            'drinks': formatted_drinks
        })
    except Exception:
        abort(422)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=['POST'])
# Requires permision post:drinks to add drinks to the database 
@requires_auth('post:drinks')
# Function to add drinks to the database
def create_drink(payload):
    body = request.get_json()
    # Get the new drink; title and reciepe
    try:
        req_title = body.get('title', None)        
        req_recipe = json.dumps(body.get('recipe', None))

        new_drink = Drink(title=req_title, recipe=req_recipe)
        # Use the insert function to add new_drink to database
        new_drink.insert()
        # format new drink to show new_drink tite, id and reciepe
        formatted_drinks = [new_drink.long()]

        return jsonify({
        'success': True,
        'drinks': formatted_drinks
        })
    except Exception:
        abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
# Requires permission patch:drinks to update drink details
@requires_auth('patch:drinks')
# Function to update detail of existing drink
def update_drink(payload, drink_id):

    body = request.get_json()

    try:
        # Query to get drink with id = drink_id
        drink_to_update = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink_to_update is None:
            abort(404)
        # Check if title is in body
        if 'title' in body:
            drink_to_update.title = body.get('title')
        # Check if recipe is in body
        if 'recipe' in body:
            drink_to_update.recipe = json.dumps(body.get('recipe'))
            
        drink_to_update.update()

        formatted_drink = [drink_to_update.long()]
        
        return({
            'success': True,
            'drinks': formatted_drink
        })

    except Exception:
        abort(400)

'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
# Requires permission delete:drinks to delete a drink from the database
@requires_auth('delete:drinks')
# Function to delete drink
def delete_drink(payload, drink_id):

    try:
        # Get drink to delete with drink id
        drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if drink is None:
            abort(404)

        drink.delete()
        
        return({
            'success': True,
            'delete': drink_id
        })

    except Exception:
        abort(422)


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
@app.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "resource not found"
    }), 400

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def authentication_error(auth_error):
    return jsonify({
        "success": False,
        "error": auth_error.status_code,
        "message": auth_error.error
    }), auth_error.status_code