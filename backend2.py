# import cv2
# import numpy as np
# import base64
# import tensorflow as tf
# from flask import Flask, render_template, request, jsonify

# app = Flask(__name__)

# # Load Models
# model_all = tf.keras.models.load_model('Model/trial_all_class_weights.h5')
# model_correct = tf.keras.models.load_model('Model/trial_correct.h5')
# model_curve = tf.keras.models.load_model('Model/trial_curve.h5')
# model_fingers_up = tf.keras.models.load_model('Model/trial_fingers_up.h5')
# model_fist = tf.keras.models.load_model('Model/trial_fist.h5')
# model_lkxy = tf.keras.models.load_model('Model/trial_lkxy.h5')
# model_point = tf.keras.models.load_model('Model/trial_point.h5')

# print("Models loaded successfully!")

# # Model mapping
# branch = {
#     0: model_fist, 1: model_fingers_up, 2: model_curve, 3: model_fingers_up,
#     4: model_fist, 5: model_correct, 6: model_point, 7: model_point,
#     8: model_fingers_up, 10: model_lkxy, 11: model_lkxy, 12: model_fist,
#     13: model_fist, 14: model_curve, 15: model_correct, 16: model_correct,
#     17: model_fingers_up, 18: model_fist, 19: model_point, 20: model_fingers_up,
#     21: model_correct, 22: model_correct, 23: model_lkxy, 24: model_lkxy
# }

# def preprocess_image(image):
#     """ Preprocess image for model prediction """
#     np_arr = np.frombuffer(image, np.uint8)
#     frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#     # Crop and resize
#     crop_img = frame[100:350, 50:300]
#     resized_img = cv2.resize(crop_img, (100, 100))

#     # Apply preprocessing
#     img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2YUV)
#     img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
#     img_hist = cv2.cvtColor(img, cv2.COLOR_YUV2RGB)
#     denoised = cv2.bilateralFilter(img_hist, 7, 100, 100)

#     # Convert to model input format
#     x_test = np.asarray(denoised).reshape((1, 100, 100, 3))
#     return x_test

# @app.route('/')
# def index():
#     """ Render the main web page """
#     return render_template('index.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     """ Handle image upload and return prediction """
#     data = request.json['image']
#     image_data = base64.b64decode(data.split(',')[1])
    
#     processed_img = preprocess_image(image_data)
#     y_pred = model_all.predict(processed_img, batch_size=1)
    
#     max_pred = np.max(y_pred)
#     predicted_char = ""
#     if max_pred > 0.5:
#         predicted_char = chr(ord('A') + np.argmax(y_pred))

#     return jsonify({'prediction': predicted_char})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8088, debug=False)



import cv2
import numpy as np
import base64
import tensorflow as tf
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
from flask_cors import CORS
CORS(app)

# Load Models
model_all = tf.keras.models.load_model('Model/trial_all_class_weights.h5')

print("Model loaded successfully!")

def preprocess_image(image):
    """ Preprocess cropped image for model prediction """
    np_arr = np.frombuffer(image, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    # Resize to match model input
    resized_img = cv2.resize(frame, (100, 100))

    # Apply preprocessing
    img = cv2.cvtColor(resized_img, cv2.COLOR_BGR2YUV)
    img[:, :, 0] = cv2.equalizeHist(img[:, :, 0])
    img_hist = cv2.cvtColor(img, cv2.COLOR_YUV2RGB)
    denoised = cv2.bilateralFilter(img_hist, 7, 100, 100)

    # Convert to model input format
    x_test = np.asarray(denoised).reshape((1, 100, 100, 3))
    return x_test

@app.route('/')
def index():
    """ Render the main web page """
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """ Handle image upload and return prediction """
    data = request.json['image']
    print("received")
    image_data = base64.b64decode(data.split(',')[1])
    
    processed_img = preprocess_image(image_data)
    y_pred = model_all.predict(processed_img, batch_size=1)
    
    max_pred = np.max(y_pred)
    predicted_char = ""
    if max_pred > 0.5:
        predicted_char = chr(ord('A') + np.argmax(y_pred))


    print(f"pred: {predicted_char}")
    return jsonify({'prediction': predicted_char})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8088, debug=False)

