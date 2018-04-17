from flask_api import FlaskAPI

from instance.config import app_config
from flask import request, jsonify, abort,session


def create_app(config_name):
    from app.models import Business
    from app.models import User
    from app.models import Review
    #create instance of flaskapi in app
    app=FlaskAPI(__name__,instance_relative_config=True)
    SESSION_TYPE = 'redis'
    app.secret_key='my-key'
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    


    
    @app.route("/")
    def welcome():
        message="Welcome to WeConnect-API"
        response=jsonify({"welcome":message})
        return response

    """AUTHENTICATION"""
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
            value_name=User.check_name_exists(username)
            validate_password=User.validate_password(password)
            validate_email=User.validate_email(email)
            validate_username=User.validate_username(username)
            validate_password_format=User.validate_password_format(password)

            if  value:

                response=jsonify({"message":"email already exists","status_code":400})
                response.status_code=400    
                return response
                return response.status_code

            elif value_name:
                response=jsonify({"message":"username already exists","status_code":400})
                response.status_code=400    
                return response
                return response.status_code

            elif validate_password:
                response=jsonify({"message":"password must be longer than 6 characters","status_code":400})
                response.status_code=400    
                return response
                return response.status_code

            elif validate_email:
                response=jsonify({"message":"Enter a valid email format","status_code":400})
                response.status_code=400    
                return response
                return response.status_code

            elif validate_username:
                response=jsonify({"message":"Username must contain characters","status_code":400})
                response.status_code=400    
                return response
                return response.status_code

            elif validate_password_format:
                response=jsonify({"message":"Password cannot be empty","status_code":400})
                response.status_code=400    
                return response
                return response.status_code





            else:
                user=User(username=username,email=email,password=password,confirm_password=confirm_password)
                message=user.save_user(username,email,password,confirm_password)
                """turn message into json"""
                response=jsonify({"message":message,"status_code":201})
                """response.status_code=201"""
                
                return response
                return response.status_code

        else:
            response=jsonify({"message":"enter all details","status_code":400})
            response.status_code=400
            return response
            return response.status_code



    @app.route('/api/v1/auth/login', methods=['POST'])
    def login():
        """this end point will log in a user based on username and password"""
        username = str(request.data.get('username', ''))
        password=str(request.data.get('password', ''))

        if username and password:
            session["username"]=username
            message=User.login(username,password)
            response=jsonify({"message":message,"status_code":200})
            return response
            

        else:
            response=jsonify({"message":"enter all details","status_code":400})
            response.status_code=400
            return response
            return response.status_code



    @app.route('/api/v1/auth/logout', methods=["POST"])
    def logout():
        """this endpoint will logout the user
        by removing them from the session"""

        if session.get("username") is not None:
            session.pop("username", None)
            return jsonify({"message": "Logout successful"})
        return jsonify({"message": "You are not logged in"})


    @app.route('/api/v1/auth/reset-password', methods=['POST'])
    def reset():
        email=str(request.data.get('email', ''))
        password=str(request.data.get('password', ''))
        confirm_password=str(request.data.get('confirm_password', ''))

        if email and password and confirm_password:
            response_message=User.reset_password(email,password,confirm_password)

            if response_message == "Password reset was successful":
                response=jsonify({"message":"password reset successfully","status_code":200})
                response.status_code=200
                return response
                return response.status_code

            elif response_message=="Password and confirm password must be the same":
                response=jsonify({"message":"password and confirm must be the same","status_code":409})
                response.status_code=409
                return response
                return response.status_code


            elif response_message ==  "Account does not exist":
                response=jsonify({"message":"password and confirm must be the same","status_code":404})
                response.status_code=404
                return response
                return response.status_code


        else:
            response=jsonify({"message":"enter all details","status_code":400})
            response.status_code=400
            return response
            return response.status_code


    """BUSINESS END POINTS"""
    @app.route('/api/v1/businesses', methods=['POST','GET'])
    def business():
        if request.method == 'POST':
            """gets data from request and save business"""

            name = str(request.data.get('name', ''))          
            description=str(request.data.get('description', ''))
            location=str(request.data.get('location', ''))
            contact=str(request.data.get('contact', ''))

            if name and description and location and contact:
                """validate that it is not duplicate"""
                validateName=Business.check_name_exists(name)
                validateContact=Business.check_contact_exists(contact)
                if validateName:
                    response=jsonify({"message":"Business name already exists","status_code":400})
                    response.status_code=400    
                    return response
                    return response.status_code

                elif validateContact:
                    response=jsonify({"message":"Business contact already exists use different contact","status_code":400})
                    response.status_code=400  
                    return response
                    return response.status_code

                
                else:
                    """create business object"""
                    business=Business(name=name,description=description,location=location,contact=contact)
                    
                    new_business=business.save_business(name,description,location,contact)

                    
                    response=jsonify(new_business)
                    response.status_code=201

                    return response

            else:
                response=jsonify({"message":"enter all details","status_code":400})
                response.status_code=400
                return response
                return response.status

        else:
            """if its a get request"""

            Businesses=Business.get_all_businesses()
            print(Businesses)
            if not Businesses:
                message="No business to display.Add a business"
                response=jsonify({"message":"business does not exist","status":200})
                response.status_code=200
                return response
            
            
            response=jsonify({"businesses":Businesses})
            response.status_code=200
            return response

                

    @app.route('/api/v1/businesses/<int:id>', methods=['GET','PUT','DELETE'])
    def business_manipulation(id):
        """gets the id of the business"""
        """uses the id to get a single business"""
        
        business_found= Business.find_business_id(id)

        if not business_found:
            response=jsonify({"message":"business does not exist","status":404})

        if request.method == "GET":
            if business_found:     
                response=jsonify({"business":business_found})
                response.status_code=200
                return response

            else:
                response=jsonify({"message":"business does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code


        elif request.method == "PUT":
            if business_found:

                name = str(request.data.get('name', ''))          
                description=str(request.data.get('description', ''))
                location=str(request.data.get('location', ''))
                contact=str(request.data.get('contact', ''))

                business_found[0]["name"] =name
                business_found[0]["description"]=description
                business_found[0]["location"]=location
                business_found[0]["contact"]=contact

                response=jsonify({"business":business_found})
                response.status_code=200
                return response

            else:
                response=jsonify({"message":"Cannot update business that does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code


        else:
            if business_found:

                businesses=Business.get_all_businesses()
                businesses.remove(business_found[0])
                response=jsonify({"business":"business successfully deleted","status":200})
                response.status_code=200
                return response
            else:
                response=jsonify({"message":"Cannot delete business that does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code



    @app.route('/api/v1/businesses/<string:name>', methods=['GET','PUT'])
    def business_manipulation_by_name(name):
        """get the id from the route"""
        """use the name to find the business"""

        business_found=Business.find_business_name(name)
        if not business_found:
            """if no business matches the name"""
            response=jsonify({"message":"business does not exist","status":404})
            response.status_code=404
            return response
            return response.status_code


        if request.method == "GET":
            if business_found:     
                response=jsonify({"Business":business_found})
                response.status_code=200
                return response

            else:
                response=jsonify({"message":"business does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code


        elif request.method == 'PUT':
            if business_found:

                name = str(request.data.get('name', ''))          
                description=str(request.data.get('description', ''))
                location=str(request.data.get('location', ''))
                contact=str(request.data.get('contact', ''))

                business_found[0]["name"] =name
                business_found[0]["description"]=description
                business_found[0]["location"]=location
                business_found[0]["contact"]=contact

                response=jsonify({"business":business_found})
                response.status_code=200
                return response

            else:
                response=jsonify({"message":"Cannot update business that does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code


        else:
            if business_found:

                businesses=Business.get_all_businesses()
                businesses.remove(business_found[0])
                response=jsonify({"business":"business successfully deleted","status":200})
                response.status_code=200
                return response
            else:
                response=jsonify({"message":"Cannot delete business that does not exist","status":404})
                response.status_code=404
                return response
                return response.status_code
    


    """REVIEWS END POINTS"""
    @app.route('/api/v1/businesses/<int:id>/reviews', methods=['POST'])
    def add_review(id):
        """get the id from the url"""
        description=str(request.data.get('description', ''))

        if description:
            """create review object"""
            new_review = Review.save_review(description,id)

            response=jsonify({"review":new_review,"status_code":201})
            response.status_code=201
            return response


        else:
            response=jsonify({"message":"enter all details","status_code":400})
            response.status_code=400
            return response
            return response.status_code


    @app.route('/api/v1/businesses/<int:id>/reviews', methods=['GET'])
    def get_reviews(id):
        reviews=Review.business_reviews(id)
            
        response=jsonify({"reviews":reviews})
        response.status_code=201
        return response        


    return app


