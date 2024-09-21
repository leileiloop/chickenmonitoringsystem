from flask import Flask, render_template, Response, jsonify, request, session, flash, url_for, redirect
#FlaskForm--> it is required to receive input from the user
# Whether uploading a video file  to our object detection model
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange
import datetime, time
import os, sys
import cv2
import numpy as np
import tensorflow as tf
from object_detection.utils import config_util
from object_detection.protos import pipeline_pb2
from google.protobuf import text_format
from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as viz_utils
from object_detection.builders import model_builder
from datetime import datetime, timedelta
import http.client
import serial
from threading import Thread
import time
from plyer import notification
from flask_socketio import SocketIO, emit

global capture
capture=0

#make shots directory to save pics
try:
    os.mkdir('static/shots')
except OSError as error:
    pass

WORKSPACE_PATH = 'Tensorflow/workspace'
SCRIPTS_PATH = 'Tensorflow/scripts'
APIMODEL_PATH = 'Tensorflow/models'
ANNOTATION_PATH = WORKSPACE_PATH+'/annotations'
IMAGE_PATH = WORKSPACE_PATH+'/images'
MODEL_PATH = WORKSPACE_PATH+'/models'
PRETRAINED_MODEL_PATH = WORKSPACE_PATH+'/pre-trained-models'
CONFIG_PATH = MODEL_PATH+'/my_ssd_mobnet/pipeline.config'
CHECKPOINT_PATH = MODEL_PATH+'/my_ssd_mobnet/'

# Load pipeline config and build a detection model
configs = config_util.get_configs_from_pipeline_file(CONFIG_PATH)
detection_model = model_builder.build(model_config=configs['model'], is_training=False)

# Restore checkpoint
ckpt = tf.compat.v2.train.Checkpoint(model=detection_model)
ckpt.restore(os.path.join(CHECKPOINT_PATH, 'ckpt-7')).expect_partial()

category_index = label_map_util.create_category_index_from_labelmap(ANNOTATION_PATH+'/label_map.pbtxt')

app = Flask(__name__)
app.config['SECRET_KEY'] = 'vince'

#Use FlaskForm to get input video file  from user
class UploadFileForm(FlaskForm):
    #We store the uploaded video file path in the FileField in the variable file
    #We have added validators to make sure the user inputs the video in the valid format  and user does upload the
    #video when prompted to do so
    file = FileField("File",validators=[InputRequired()])
    submit = SubmitField("Run")

# -------------Camera-------------

# Path to the "shots" folder
shots_folder = os.path.join(os.path.dirname(__file__), 'static/shots')

# Get a list of image files in the "shots" folder
image_files = [f for f in os.listdir(shots_folder) if f.endswith(('jpg', 'jpeg', 'png', 'gif'))]

healthy_count = 0
sick_count = 0

def generate_frames_web():

    global healthy_count
    global sick_count

    @tf.function
    def detect_fn(image):
        image, shapes = detection_model.preprocess(image)
        prediction_dict = detection_model.predict(image, shapes)
        detections = detection_model.postprocess(prediction_dict, shapes)
        return detections

    # Setup capture
    cap = cv2.VideoCapture(0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    global capture

    while True:

        try:
            ret, frame = cap.read()
            image_np = np.array(frame)

            input_tensor = tf.convert_to_tensor(np.expand_dims(image_np, 0), dtype=tf.float32)
            detections = detect_fn(input_tensor)

            num_detections = int(detections.pop('num_detections'))
            detections = {key: value[0, :num_detections].numpy() for key, value in detections.items()}
            detections['num_detections'] = num_detections
            detections['detection_classes'] = detections['detection_classes'].astype(np.int64)

            label_id_offset = 1
            image_np_with_detections = image_np.copy()

            # Visualize bounding boxes and labels on the image
            viz_utils.visualize_boxes_and_labels_on_image_array(
                image_np_with_detections,
                detections['detection_boxes'],
                detections['detection_classes'] + label_id_offset,
                detections['detection_scores'],
                category_index,
                use_normalized_coordinates=True,
                max_boxes_to_draw=5,
                min_score_thresh=.5,
                agnostic_mode=False)

            # Import the necessary libraries for displaying text on the image
            font = cv2.FONT_HERSHEY_SIMPLEX
            org = (10, 25)  # Origin point for the text
            font_scale = 1
            font_color = (255, 255, 255)  # White color in BGR
            font_thickness = 1

            for i in range(num_detections):
                detected_class = detections['detection_classes'][i] + label_id_offset
                detected_score = detections['detection_scores'][i]

                # Debug print statements
                print(f'Detected Class: {detected_class}, Score: {detected_score}')

                if detected_class == 1:  # Class ID for 'hatched_egg'
                    if detected_score >= 0.5:  # Check if the detection is not in the set
                        healthy_count += 1

                        print(f'Healthy Count: {healthy_count}')

                        # Get the current date and time
                        current_datetime = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')

                        # Define the width and height of the rectangle based on the expected text size
                        rectangle_width = 800  # Adjust as needed
                        rectangle_height = 600  # Adjust as needed

                        # Draw a black rectangle as a background for the text
                        cv2.rectangle(image_np_with_detections, org,
                                          (org[0] + rectangle_width, org[1] - rectangle_height),
                                          (0, 0, 0), -1)

                        # Display date and time on the image
                        cv2.putText(image_np_with_detections, f'Date and Time: {current_datetime}', org, font,
                                        font_scale,
                                        font_color, font_thickness, cv2.LINE_AA)

                        # Set the flag to initiate capture
                        capture = 1


                    elif detected_class == 2:  # Class ID for 'unhatched_egg'
                        if detected_score >= 0.5 :  # Check if the detection is not in the set

                            sick_count += 1

                            print(f'Sick Count: {sick_count}')

                if capture:
                    capture = 0
                    now = datetime.now()
                    filename = "shot_{}.png".format(str(now).replace(":", ''))
                    # Assuming the static folder is in the same directory as your script
                    p = os.path.join('static', 'shots', filename)
                    cv2.imwrite(p, image_np_with_detections)

                ret, buffer = cv2.imencode('.jpg', image_np_with_detections)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        except http.client.IncompleteRead as e:
            print(f"An error occurred while reading the video stream: {e}")
            continue

# ---------------Login Form---------------


@app.route('/', methods=['GET','POST'])
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
    return render_template('login.html', error='', image_files=image_files)

# ---------------Dashboard---------------


@app.route("/dashboard", methods=['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html', image_files=image_files)

# ---------------Growth Monitoring---------------


@app.route("/webcam", methods=['GET', 'POST'])
def webcam():
    return render_template('growth.html', image_files=image_files)


@app.route('/webapp')
def webapp():
    return Response(generate_frames_web(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Global variables for data table
current_frame = None
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
    # Implement your logic to add a meal to the schedule
    # For example, appending a dictionary to the list
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

    return render_template('feed.html', meal_schedule=meal_schedule, image_files=image_files)


# ---------------Environment---------------


@app.route("/environment", methods=['GET', 'POST'])
def environment():
    return render_template('environment.html', image_files=image_files)

# ---------------Sanitization---------------


@app.route("/sanitization", methods=['GET', 'POST'])
def sanitization():
    return render_template('sanitization.html', image_files=image_files)

# ---------------Image List---------------


@app.route('/get_image_list')
def get_image_list():
    shots_folder = os.path.join(app.static_folder, 'shots')
    image_files = [f for f in os.listdir(shots_folder) if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))]
    return jsonify(image_files)

# ---------------Capture Image---------------

@app.route('/requests1', methods=['POST'])
def capture():
    if request.method == 'POST' and 'click' in request.form and request.form['click'] == 'Capture':
        # Capture logic (replace this with your actual capture code)
        # For example, you can use OpenCV to capture a frame from the camera
        # and save it to the 'static/shots' directory

        # Sample code (make sure to adapt this to your actual capture logic)
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        filename = os.path.join(shots_folder, f'captured_image_{time.time()}.jpg')
        cv2.imwrite(filename, frame)
        cap.release()

        return 'Capture successful'
    else:
        return 'Invalid request'

@app.route('/requests',methods=['POST','GET'])
def tasks():
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1

            print("Capture initiated")
    elif request.method == 'GET':
        return render_template('growth.html', image_files=image_files)
    return render_template('growth.html', image_files=image_files)

# Define a route to get the egg counts
@app.route('/chick_counts')
def egg_counts():
    global healthy_count
    global sick_count
    return {
        'hatched_egg_count': healthy_count,
        'unhatched_egg_count': sick_count
    }


if __name__ == '__main__':
    app.run(debug=True)
