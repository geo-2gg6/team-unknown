import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

# --- App Configuration ---
# Get the absolute path of the directory containing this file.
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# A secret key is required for sessions and flash messages.
app.config['SECRET_KEY'] = 'a-very-secret-and-hard-to-guess-key'
# Configure the SQLite database, placing it in the project directory.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
# If a user tries to access a protected page without being logged in,
# they will be redirected to the 'login' page.
login_manager.login_view = 'login'


# --- Database Model ---
# The User model defines the structure of our 'user' table in the database.
# UserMixin provides default implementations for session management methods.
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(150), nullable=False)

    def set_password(self, password):
        """Hashes the password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

# This function is required by Flask-Login to load a user from the session.
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# --- Routes ---
@app.route('/')
def home():
    # The home page simply redirects to the login page.
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # If the user is already logged in, redirect them to the dashboard.
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Find the user in the database by their username.
        user = User.query.filter_by(username=username).first()

        # If the user exists and the password is correct...
        if user and user.check_password(password):
            login_user(user) # Log the user in.
            return redirect(url_for('dashboard'))
        else:
            # Otherwise, show an error message.
            flash('Invalid username or password. Please try again.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if a user with that username already exists.
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'warning')
            return redirect(url_for('register'))
        
        # Create a new user, set their password, and save to the database.
        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/dashboard')
@login_required # This decorator protects the page, requiring login.
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user() # Log the user out.
    flash('You have been successfully logged out.', 'success')
    return redirect(url_for('login'))

# --- Main Execution ---
if __name__ == '__main__':
    # This block ensures that the database and tables are created
    # before the first request to the app.
    with app.app_context():
        db.create_all()
    app.run(debug=True)
