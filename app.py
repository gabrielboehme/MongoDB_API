from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import pymongo
import bcrypt
from datetime import datetime

#App settings
app = Flask(__name__)
api = Api(app)

#DB settings

client = pymongo.MongoClient('localhost', 27017)
db = client.SentencesDB
users = db['Users']

#Register endpoint
class Register(Resource):

    def post(self):

        #Get posted data from user
        posted_data = request.get_json()

        #Username and Psw
        username = posted_data["username"]
        psw = posted_data["password"]

        #Hashing the psw
        hashed_psw = bcrypt.hashpw(psw.encode('utf8'), bcrypt.gensalt())

        #Storing in the db
        users.insert_one({
            "Username": username,
            "Password": hashed_psw,
            "Sentence":"",
            "Creation_Date": datetime.now().strftime("%d-%m-%Y"),
            "tokens": 10
        })

        #returning

        ret_json = {
            "status": 200,
            "message": "You sucessfully signed up for the API!"
        }

        return jsonify(ret_json)

#Store endpoint

def verify_login(username, psw):

    #getting the stored psw
    hashed_psw = users.find({
        "Username":username
    })[0]['Password']

    #Checking equality
    if bcrypt.hashpw(psw.encode('utf8'), hashed_psw)==hashed_psw:

        return True

    else:

        return False

def count_tokens(username):

    #getting nb of tokens from username
    tokens  = users.find({
        "Username": username
    })[0]["tokens"]

    return tokens


class Store(Resource):

    def post(self):

        #Get posted data from user
        posted_data = request.get_json()

        #Read the data
        username = posted_data["username"]
        psw = posted_data["password"]
        sentence = posted_data["sentence"]

        #Verify login
        correct_psw = verify_login(username, psw)
        
        if not correct_psw:
            
            ret_json = {"status": 302}

            return jsonify(ret_json)

        #Verify enought tokens
        enought_tokens = count_tokens(username)

        if not enought_tokens>0:
            
            ret_json = {"status": 301}

            return jsonify(ret_json)

        #Store sentence, retrieve 1 token and return status 200
        users.update({
            "Username":username},
                {
                "$set":{
                    "Sentence": sentence,
                    "tokens": (enought_tokens-1)
                        }
        })

        ret_json = {
            "status": 200,
            "message": "You sucessfully signed up for the API!"
        }

        return jsonify(ret_json)


#Get endpoint
class Get(Resource):

    def post(self):

        #get user posted data
        posted_data = request.get_json()

        #get username and psw
        username = posted_data['username']
        psw = posted_data['password']


        correct_psw = verify_login(username, psw)
        #verify login
        if not correct_psw:
            
            ret_json = {"status": 302}

            return jsonify(ret_json)

        enought_tokens = count_tokens(username)
        if not enought_tokens>0:
            
            ret_json = {"status": 301}

            return jsonify(ret_json)
        
        sentence = users.find({"Username": username})[0]['Sentence']

        users.update({
            "Username":username},
                {
                "$set":{
                    "Sentence": sentence,
                    "tokens": (enought_tokens-1)
                        }
})

        ret_json = {
            "status":200,
            "sentence": sentence,
            "tokens": (enought_tokens-1)
            }

        return jsonify(ret_json)

api.add_resource(Register, '/register')
api.add_resource(Store, '/store')
api.add_resource(Get, '/get')

if __name__ == '__main__':
    app.run(debug=True)