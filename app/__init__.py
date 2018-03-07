from flask_api import FlaskAPI

from instance.config import app_config
from flask import request, jsonify, abort

def create_app(config_name):
    from app.models import Business
    from app.models import User
    #create instance of flaskapi
    app=FlaskAPI(__name__,instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')


    
    @app.route(/)
    def welcome():
        message="Welcome to WeConnect-API"
        response=jsonify({"welcome":message})
        return response









    #api functionality
    @app.route('/api/v1/auth/register', methods=['POST'])
    def register():
        """ 
        This end point will register a user by getting info from the request
        """
        username = str(request.data.get('username', ''))          
        email=str(request.data.get('email', ''))
        password=str(request.data.get('password', ''))
        confirm_password=str(request.data.get('confirm_password', ''))

        if username and email and password and confirm_password:
            value=User.check_email_exists(email)

            if  value:

                response=({"message":"email already exists","status_code":409})

                # response.status_code=409     
                return response
            else:
                user=User(username=username,email=email,password=password,confirm_password=confirm_password)
                message=user.save_user(username,email,password,confirm_password)
                """turn message into json"""
                response=jsonify({"message":message,"status_code":201})
                # response.status_code=201
                # response_message=jsonify({"status code":response.status_code})
                return response
                return response.status_code











            
    

    return app


