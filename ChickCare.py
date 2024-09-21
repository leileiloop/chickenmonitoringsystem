from flask import Flask, render_template, jsonify, request, session, flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vince'

#Use FlaskForm to get input video file from user
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Run")

# ---------------Login Form---------------

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username is not None and password is not None:
            # Validate the credentials (replace with your actual validation logic)
            if username == 'admin' and password == 'admin':
                # Successful login, redirect to the dashboard
                return redirect(url_for('dashboard'))

        # Invalid credentials or form not fully filled, display error message
        return render_template('login.html', error='Invalid credentials')

    # For GET requests (initial page load), render the login page without an error
    return render_template('login.html', error='')

# ---------------Dashboard---------------

@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

# ---------------Growth Monitoring---------------

@app.route("/webcam", methods=['GET', 'POST'])
def webcam():
    return render_template('growth.html')

# Global variables for data table
table_data = [
    {"Days": 1, "Size": 10, "Weight": 50},
    {"Days": 2, "Size": 15, "Weight": 60},
    {"Days": 3, "Size": 20, "Weight": 70},
    # Add more data as needed
]

# Route for table data
@app.route('/table_data')
def get_table_data():
    return {"data": table_data}

# ---------------Feeding Schedule---------------
# Placeholder for meal schedule data
meal_schedule = []

def add_meal(schedule, date_time, meal):
    schedule.append({"Date/Time": date_time, "Meal": meal})
    return schedule

@app.route("/feeding", methods=['GET', 'POST'])
def feeding():
    global meal_schedule

    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        meal = request.form['meal']
        meal_schedule = add_meal(meal_schedule, date, time, meal)

    return render_template('feed.html', meal_schedule=meal_schedule)

# ---------------Environment---------------

@app.route("/environment", methods=['GET', 'POST'])
def environment():
    return render_template('environment.html')

# ---------------Sanitization---------------

@app.route("/sanitization", methods=['GET', 'POST'])
def sanitization():
    return render_template('sanitization.html')

# ---------------Image List---------------

@app.route('/get_image_list')
def get_image_list():
    # Return an empty list as local storage is not supported in Vercel
    return jsonify([])

# Define a route to get the egg counts
@app.route('/chick_counts')
def egg_counts():
    # Placeholder values
    healthy_count = 0
    sick_count = 0
    return {
        'hatched_egg_count': healthy_count,
        'unhatched_egg_count': sick_count
    }

if __name__ == '__main__':
    app.run(debug=True)
