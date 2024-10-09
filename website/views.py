
from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from .models import User
from .models import PredictionReport
import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename 
from . import db

import cv2


views = Blueprint("views", __name__)

@views.route("/home")
@login_required
def home():
    print(f"Current user: {current_user}")
    return render_template("home.html", name=current_user.username)

@views.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if not current_user.is_admin:
        flash('You do not have permission to access the dashboard.', category='error')
        return redirect(url_for('views.home'))

    # Query to get all users who are not admin
    non_admin_users = User.query.filter_by(is_admin=False).all()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        user_to_delete = User.query.get(user_id)
        if user_to_delete:
            db.session.delete(user_to_delete)
            db.session.commit()
            flash(f'User {user_to_delete.username} has been deleted.', 'success')
            return redirect(url_for('views.dashboard'))  # Reload the page to reflect changes

    return render_template("dashboard.html", users=non_admin_users)

# @views.route("/dashboard")
# @login_required
# def dashboard():
#     if not current_user.is_admin:
#         flash('You do not have permission to access the dashboard.', category='error')
#         return redirect(url_for('views.home'))
#     print(f"Current user: {current_user}")
#     return render_template("dashboard.html")

# @views.route('/getuser', methods=['GET', 'POST'])
# @login_required
# def getuser():
#     # Query to get all users who are not admin
#     non_admin_users = User.query.filter_by(is_admin=False).all()

#     if request.method == 'POST':
#         user_id = request.form.get('user_id')
#         # username = request.form.get('username')
#         user_to_delete = User.query.get(user_id)
#         if user_to_delete:
#             db.session.delete(user_to_delete)
#             db.session.commit()
#             flash(f'User {user_to_delete.username} deleted.', 'success')
#             return redirect(url_for('views.getuser'))

#     return render_template('dashboard.html', users=non_admin_users)


# def delete_user(user_id):
#     if not current_user.is_admin:
#         flash('You do not have permission to perform this action.', category='error')
#         return redirect(url_for('views.home'))

#     user_to_delete = User.query.get(user_id)
#     if user_to_delete:
#         db.session.delete(user_to_delete)
#         db.session.commit()
#         flash(f'User {user_to_delete.username} has been deleted.', category='success')
#     else:
#         flash('User not found.', category='error')

#     return redirect(url_for('views.dashboard'))

@views.route("/about")
@login_required
def about():
    print(f"Current user: {current_user}")
    return render_template("about.html", name=current_user.username)

@views.route("/contact")
@login_required
def contact():
    print(f"Current user: {current_user}")
    return render_template("contact.html", name=current_user.username)

@views.route("/predict", methods=['GET', 'POST'])
@login_required


def predict():

    
    
    if not current_user.is_admin:
        flash('You do not have permission to access the prediction page.', category='error')
        return redirect(url_for('views.home'))

    if request.method == 'POST':
        email = request.form.get('user-email')
        if 'file' not in request.files:
            flash('No file part', category='error')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', category='error')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            # Preprocess the image
            img = cv2.imread(file_path)
            IMAGE_SIZE = (128, 128)
            scaled_image = tf.image.resize(img, IMAGE_SIZE)

            # Convert to grayscale if necessary
            if scaled_image.shape[-1] == 3:
                scaled_image = tf.image.rgb_to_grayscale(scaled_image)

            # Normalize and reshape the image
            scaled_image = scaled_image / 255.0
            scaled_image = np.expand_dims(scaled_image, axis=0)  # Add batch dimension
            scaled_image = np.expand_dims(scaled_image, axis=-1)  # Add channel dimension

            # Make prediction
            model = current_app.model
            class_names = current_app.class_names
            yhat = model.predict(scaled_image)

            # Determine the class based on threshold
            print(yhat)
            prediction = class_names[1] if yhat[0] > 0.05 else class_names[0]
            
            flash(f'Prediction: {prediction}', category='error')
            print(f'Prediction: {prediction}')
            
            # Save the prediction result to the PredictionReport table
            prediction_report = PredictionReport(
                email=email,  # Assuming admin is logged in and making predictions
                filename=filename,
                prediction=prediction
            )
            db.session.add(prediction_report)
            db.session.commit()
            
            flash(f'Prediction saved successfully!', category='success')
            
            predicted_label = prediction
            return redirect(url_for('views.predict'))

    return render_template("predict.html")

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




