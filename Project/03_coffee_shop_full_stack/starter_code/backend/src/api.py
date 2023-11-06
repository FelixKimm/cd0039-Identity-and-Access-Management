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
def get_drinks():

    drinks = Drink.query.all()

    short_drink = [drink.short() for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': short_drink
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):

    drinks = Drink.query.all()

    long_drink = [drink.long()for drink in drinks]

    return jsonify({
        'success': True,
        'drinks': long_drink
    })

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks', methods=["POST"])
@requires_auth('post:drinks')
def post_drinks(payload):

    body = request.get_json()

    new_title = body.get('title', None)
    new_recipe = body.get('recipe', None)

    if not ('title' in body and 'recipe' in body):
        abort(422)
    
    try:
        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink.insert()

    except:
        abort(422)
    
    return jsonify({
        'success': True,
        'drinks': [new_drink.long()]
    })

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
@app.route('/drinks/<int:id>', methods=["PATCH"])
@requires_auth('patch:drinks')
def patch_drinks(paylods, id):
    
    body = request.get_json()

    patch_drink = Drink.query.get(id)

    patch_title = body.get('title', None)
    patch_recipe = body.get('recipe', None)

    if patch_drink == None:
        abort(404)

    if patch_title:
        patch_drink.title = patch_title

    if patch_recipe:
        patch_drink.recipe = json.dumps(patch_recipe)

    return jsonify({
        "success": True,
        "drinks": [patch_drink.long()]
    })

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

@app.route('/drinks/<int:id>', methods=["DELETE"])
@requires_auth('delete:drinks')
def patch_drinks(paylods, id):

    try:
        delete_drink = Drink.query.get(id)

        if delete_drink == None:
            abort(404)

        delete_drink.delete()

        return jsonify({
            "success": True,
            "delete": id
        })
        
    except:
        abort(422)



# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({"success": False, "error": 400, "message": "bad request"}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({"success": False, "error": 404, "message": "resource not found"}), 404

@app.errorhandler(405)
def not_allowed(error):
    return jsonify({"success": False, "error": 405, "message": "method not allowed"}), 405

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({"success": False, "error": 422, "message": "unprocessable"}), 422

@app.errorhandler(500)
def server_error(error):
    return jsonify({"success": False, "error": 500, "message": "server error"}), 500


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def autherror():
    return jsonify({"success": False, "error": 401, "message": "server error"}), 401