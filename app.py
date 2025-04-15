# Import necessary libraries and modules
from dotenv import load_dotenv
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, verify_jwt_in_request
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, User, Subscription
from flasgger import Swagger
import datetime
from models import db, User, Subscription
from flask_cors import CORS

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing (CORS) for all routes
CORS(app)

# ------------------- CONFIGURATION ------------------- #
# Set up application configurations
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/eliteit'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')  # Secret key for JWT
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# ------------------- SWAGGER CONFIGURATION ------------------- #
# Set up Swagger UI for API documentation
swagger = Swagger(app, template={
    "swagger": "2.0",
    "info": {
        "title": "EliteIT API",
        "description": "API documentation for authentication, subscription, and profile management.",
        "version": "1.0.0"
    },
    "basePath": "/"
})


# Initialize the blacklist for JWT token revocation
blacklist = set()

# ------------------- EXTENSIONS INITIALIZATION ------------------- #
# Initialize the necessary extensions: database, JWT, and migration
db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Create tables in the database (only once on app startup)
with app.app_context():
    db.create_all()

# ------------------- ROUTES ------------------- #

# ------------------- AUTH ------------------- #

# User Registration Route
@app.route('/register', methods=['POST'])
def register():
    """User Registration
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
            confirm_password:
              type: string
    responses:
      201:
        description: User registered successfully
      400:
        description: Missing fields or password mismatch
      409:
        description: User already exists
    """
    email = request.json.get('email')
    password = request.json.get('password')
    confirm_password = request.json.get('confirm_password')

    # Validate input fields
    if not email or not password or not confirm_password:
        return jsonify({'msg': 'Missing required fields'}), 400
    if password != confirm_password:
        return jsonify({'msg': 'Passwords do not match'}), 400

    # Check if user already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'msg': 'User already exists'}), 409

    # Hash the password and create new user
    hashed_password = generate_password_hash(password)
    new_user = User(email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'msg': 'User registered successfully'}), 201

# User Login Route
@app.route('/login', methods=['POST'])
def login():
    """User Login
    ---
    tags:
      - Authentication
    consumes:
      - application/json
    parameters:
      - in: body
        name: credentials
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            password:
              type: string
    responses:
      200:
        description: Login successful
      401:
        description: Invalid credentials
    """
    email = request.json.get('email')
    password = request.json.get('password')

    # Validate input fields
    if not email or not password:
        return jsonify({'msg': 'Missing required fields'}), 400

    # Check user credentials
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'msg': 'Invalid credentials'}), 401

    # Generate access and refresh tokens
    access_token = create_access_token(identity=email, fresh=True)
    refresh_token = create_refresh_token(identity=email)

    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token
    }), 200

# Token Refresh Route
@app.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh JWT token
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: New access token
    """
    current_user = get_jwt_identity()
    access_token = create_access_token(identity=current_user)
    return jsonify({'access_token': access_token}), 200

# User Logout Route
@app.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout User (Revoke Token)
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Successfully logged out
    """
    jti = get_jwt()['jti']
    blacklist.add(jti)
    return jsonify({'msg': 'Successfully logged out'}), 200

# Check if JWT token is blacklisted
@app.before_request
def check_blacklist():
    # Public paths for Swagger UI and static assets
    public_paths = [
        '/apidocs', '/apidocs/', '/apispec_1.json', '/static', '/favicon.ico',
        '/flasgger_static', '/flasgger_static/'
    ]

    # Allow access to public paths without JWT
    if any(request.path.startswith(path) for path in public_paths) or request.endpoint in ['login', 'register', 'home']:
        return None

    # For all other routes, enforce JWT check
    verify_jwt_in_request()
    jti = get_jwt()['jti']
    if jti in blacklist:
        return jsonify({'msg': 'Token has been revoked'}), 401


# ------------------- SUBSCRIPTION ------------------- #
# Subscribe to a plan
@app.route('/subscribe', methods=['POST'])
@jwt_required()
def subscribe():
    """Subscribe to a plan
    ---
    tags:
      - Subscription
    consumes:
      - application/json
    security:
      - Bearer: []
    parameters:
      - in: body
        name: plan
        required: true
        schema:
          type: object
          properties:
            plan_type:
              type: string
              enum: [freebie, professional, enterprise]
    responses:
      201:
        description: Subscription created or upgraded
      400:
        description: Invalid request
    """
    email = get_jwt_identity()
    plan = request.json.get('plan_type')

    if not plan:
        return jsonify({'msg': 'Missing plan type'}), 400

    # Fetch the user 
    user = User.query.filter_by(email=email).first()

    # Fetch the current active subscription
    current_sub = Subscription.query.filter_by(user_id=user.id, is_active=True).first()

    # If no active subscription exists, allow subscription
    if current_sub is None:
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)

        new_subscription = Subscription(
            user_id=user.id,
            plan_type=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        db.session.add(new_subscription)

        try:
            db.session.commit()
            return jsonify({'msg': f'Subscribed successfully to the "{plan}" plan.'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'msg': f'Error: {str(e)}'}), 500

    # Handle upgrades and downgrades:
    if current_sub.plan_type == 'freebie' and plan in ['professional', 'enterprise']:
        # Freebie users can always upgrade to Professional or Enterprise
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)

        new_subscription = Subscription(
            user_id=user.id,
            plan_type=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        # Deactivate the current Freebie plan and add new subscription
        current_sub.is_active = False
        db.session.add(new_subscription)

        try:
            db.session.commit()
            return jsonify({'msg': f'Upgraded to the "{plan}" plan successfully.'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'msg': f'Error: {str(e)}'}), 500

    # Handle Professional plan to Enterprise upgrade with confirmation
    elif current_sub.plan_type == 'professional' and plan == 'enterprise':
        days_left = (current_sub.end_date - datetime.date.today()).days
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)

        new_subscription = Subscription(
            user_id=user.id,
            plan_type=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        # Deactivate the current Freebie plan and add new subscription
        current_sub.is_active = False
        db.session.add(new_subscription)

        try:
            db.session.commit()
            return jsonify({'msg': f'Upgraded to the "{plan}" plan successfully.'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'msg': f'Error: {str(e)}'}), 500

    # Downgrading from Professional to Freebie or Enterprise to Professional
    elif current_sub.plan_type == 'professional' and plan == 'freebie':
        days_left = (current_sub.end_date - datetime.date.today()).days
        return jsonify({
            'msg': f'You cannot downgrade from Professional to Freebie. You have to wait {days_left} days.'
        }), 400

    # Prevent downgrade from Enterprise to Freebie
    elif current_sub.plan_type == 'enterprise' and plan == 'freebie':
        days_left = (current_sub.end_date - datetime.date.today()).days
        return jsonify({
            'msg': f'You cannot downgrade from Enterprise to Freebie. You have to wait {days_left} days.'
        }), 400

    # Prevent downgrade from Enterprise to Professional
    elif current_sub.plan_type == 'enterprise' and plan == 'professional':
        days_left = (current_sub.end_date - datetime.date.today()).days
        return jsonify({
            'msg': f'You cannot downgrade from Enterprise to Professional. You have to wait {days_left} days.'
        }), 400

    # If the user wants to change to a different plan, and there's no specific logic:
    # Deactivate previous active subscription and create a new one
    if current_sub.plan_type != plan:
        # Update the current plan based on the user's confirmation
        current_sub.is_active = False
        start_date = datetime.date.today()
        end_date = start_date + datetime.timedelta(days=30)

        new_subscription = Subscription(
            user_id=user.id,
            plan_type=plan,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )

        db.session.add(new_subscription)
        try:
            db.session.commit()
            return jsonify({'msg': f'Subscribed successfully to the "{plan}" plan.'}), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'msg': f'Error: {str(e)}'}), 500

    return jsonify({'msg': f'You are already subscribed to the "{plan}" plan.'}), 409

# ------------------- PROFILE ------------------- #

# Get User Profile
@app.route('/profile', methods=['GET'])
@jwt_required()
def profile():
    """Get User Profile
    ---
    tags:
      - Profile
    security:
      - Bearer: []
    responses:
      200:
        description: User profile data
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()
    sub = Subscription.query.filter_by(user_id=user.id, is_active=True).first()

    return jsonify({
        'name': user.name,
        'email': user.email,
        'city': user.city,
        'state': user.state,
        'pin_code': user.pin_code,
        'logo': user.logo,
        'gst_number': user.gst_number,
        'profile_photo': user.profile_photo,
        'subscription': {
            'plan': sub.plan_type if sub else None,
            'start_date': str(sub.start_date) if sub else None,
            'end_date': str(sub.end_date) if sub else None,
            'is_active': sub.is_active if sub else False
        }
    }), 200

# Update User Profile
@app.route('/update-profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """
    Update Profile
    ---
    tags:
      - Profile
    consumes:
      - application/json
    parameters:
      - name: name
        in: body
        type: string
        required: false
        description: User's full name
      - name: city
        in: body
        type: string
        required: false
        description: City name
      - name: state
        in: body
        type: string
        required: false
        description: State name
      - name: pin_code
        in: body
        type: string
        required: false
        description: ZIP or postal code
      - name: gst_number
        in: body
        type: string
        required: false
        description: GST number
    responses:
      200:
        description: Profile updated successfully
    security:
      - Bearer: []
    """
    email = get_jwt_identity()
    user = User.query.filter_by(email=email).first()

    # Get JSON data
    data = request.get_json()

    # Extract fields from the JSON body
    name = data.get('name')
    city = data.get('city')
    state = data.get('state')
    pin_code = data.get('pin_code')
    gst_number = data.get('gst_number')

    # Update fields if they are provided
    if name:
        user.name = name
    if city:
        user.city = city
    if state:
        user.state = state
    if pin_code:
        user.pin_code = pin_code
    if gst_number:
        user.gst_number = gst_number

    # Commit changes to the database
    db.session.commit()

    return jsonify({'msg': 'Profile updated successfully'}), 200


# ------------------- ADMIN ------------------- #


# Admin route to view expired subscriptions
@app.route('/admin', methods=['GET'])
@jwt_required()
def expired_subscriptions():
    """Get Expired Subscriptions (Admin Only)
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: List of expired or inactive subscriptions
    """
    email = get_jwt_identity()

    if email != 'admin@example.com':
        return jsonify({'msg': 'Access denied'}), 403

    today = datetime.date.today()
    expired = Subscription.query.filter(
        (Subscription.end_date < today) | (Subscription.is_active == False)
    ).all()

    result = []
    for sub in expired:
        user = User.query.get(sub.user_id)
        result.append({
            'email': user.email,
            'plan': sub.plan_type,
            'end_date': str(sub.end_date),
            'is_active': sub.is_active
        })

    return jsonify({'expired_subscriptions': result}), 200

# ------------------- MAIN ------------------- #
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

