from flask import Flask
from models import db, User, Subscription

app = Flask(__name__)

# Replace 'username', 'password', and 'mydatabase' with your actual MySQL user, password, and database name
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:password@localhost/eliteit'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
