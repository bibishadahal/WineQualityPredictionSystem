
from flask import Flask, render_template, request, redirect, session, url_for,jsonify
import mysql.connector
import joblib
from joblib import load
import pandas as pd
from decision_tree_functions import decision_tree_algorithm, decision_tree_predictions
from random_forest import random_forest_predictions

app = Flask(__name__)
app.secret_key = "super secret key"

conn = mysql.connector.connect(host="localhost", user="root", password="", database="project")
cursor = conn.cursor()
# wine_predictor = WineQualityPredictor()
model = joblib.load('trained_model.joblib')

from flask import redirect, session

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        # You may want to add validation for the input fields here
        
        try:
            # Check if the username or email already exists in the database
            cursor.execute('SELECT * FROM user1 WHERE username=%s OR email=%s', (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                return "Username or email already exists."
            
            # Insert the new user into the database
            cursor.execute('INSERT INTO user1 (username, email, password) VALUES (%s, %s, %s)', (username, email, password))
            conn.commit()
            
            # Set session variables for the newly registered user
            session['loggedin'] = True
            session['username'] = username
            
            return redirect(url_for('login'))  # Redirect to login page after successful registration
        except Exception as e:
            print(e)
            return "Registration failed. Please try again later."
    
    return render_template('registration.html')



@app.route("/")
def index():
    return render_template("login.html")

@app.route("/home")
def home():
    return render_template('home.html', username=session.get('username'))

@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute('SELECT * FROM user1 WHERE username=%s AND password=%s', (username, password))
        record = cursor.fetchone()
        if record:
            session['loggedin'] = True
            session['username'] = record[1]
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username or password'
            return render_template('login.html', msg=msg)
    return render_template('login.html', msg="+-")



@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get input data from frontend
        data = request.get_json()

        for key, value in data.items():
            data[key] = float(value)

        # Convert data to DataFrame
        input_data = pd.DataFrame(data, index=[0])
      
        # Perform prediction using the random forest model
        predictions = random_forest_predictions(input_data, model)

        # Return both input data and prediction
        return jsonify({"input_data": data, "prediction": predictions[0]})
    except Exception as e:
        print(e)
        return jsonify({'error': "Prediction failed"})

    



@app.route('/result')
def result():
    prediction = request.args.get('prediction')
    input_data = dict(request.args)
    input_data.pop('prediction')  # Remove the prediction from input_data
    return render_template('result.html', prediction=prediction, input_data=input_data)



    

if __name__ == '__main__':
    app.run(debug=True) 


