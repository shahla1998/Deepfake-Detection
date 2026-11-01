import streamlit as st
from PIL import Image
import numpy as np
import datetime
import cv2
import tempfile
import database
import os
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image as keras_image
from database import init_db, log_prediction, fetch_history

database.init_db()

st.title("Deepfake Detection App")
st.write("Welcome! Upload an image / video below to check whether fit is Real or Fake")

@st.cache_resource
def load_my_model():
    model = load_model('deepfake_detection_model.h5')
    return model

model = load_my_model()

uploaded_file = st.file_uploader("Choose an image or video...", type=["jpg", "jpeg", "png", "mp4", "mov", "avi"])

if uploaded_file is not None:
    file_name = uploaded_file.name.lower()

    if file_name.endswith(('.jpg', '.jpeg', '.png')):
        st.subheader("Image Deepfake Detector")
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_container_width = True)

        if st.button('Predict Image'):
             with st.spinner('Analyzing the image... Please wait...'):
                 img = image.resize((128, 128))
                 img_array = keras_image.img_to_array(img)
                 img_array = np.expand_dims(img_array, axis=0) / 255.0

                 prediction = model.predict(img_array)
                 score = prediction[0][0]
                 print("Model Raw Score:", score)

                 if score > 0.5:
                      result = "Fake"
                      confidence = float(score) * 100

                
                 else:
                      result = "Real"

                 st.success(f"Prediction: **{result}**")
                 st.info(f"Confidence: **{confidence:.2f}%**")

                 current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                 database.log_prediction(uploaded_file.name, result, confidence)
                 st.toast("Result saved to database successfully!", icon='✅')

    elif file_name.endswith(('.mp4', '.mov', '.avi')):
        st.subheader("Video Deepfake Detector(OpenCV Powered)")

        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(video_bytes :=uploaded_file.read())
        video_path = tfile.name

        st.video(uploaded_file)

        if st.button("Analyze Video"):
            with st.spinner('Processing video frame using OpenCV... Please wait...'):
                cap = cv2.VideoCapture(video_path)
                frame_count = 0
                fake_score = []

                face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

                while cap.isOpened():
                    ret, frame = cap.read()
                    if not ret:
                        break

                    if frame_count % 30 == 0:
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

                        for (x, y, w, h) in faces:
                            face_crop = frame[y:y+h, x:x+w]
                            try:
                                face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                                img_pil = Image.fromarray(face_rgb).resize((128, 128))
                                iimg_array = keras_image.img_to_array(img_pil)
                                img_array = np.expand_dims(img_array, axis=0) / 255.0

                                prediction = model.predict(img_array)
                                fake_scores.append(prediction[0][0])
                            except Exception as e:
                                pass

                    frame_count += 1

                cap.release()

                if len(fake_scores) > 0:
                    avg_score = np.mean(fake_scores)   
                    if avg_score > 0.5:
                        video_result = "Fake Video"
                        vid_conf = float(avg_score) * 100
                    else:
                        video_result = "Real Video"
                        vid_conf = (1 - float(avg_score)) * 100

                    st.success(f"Video Analysis Result: **{video_result}**")
                    st.info(f"Average Confidence: **{vid_conf:.2f}**")
                    database.log_prediction(uploaded_file.name, video_result, vid_conf) 
                    st.toast("Video result saved to database successfully!", icon='✅')

                else:
                    st.warning("Could not detect faces clearly in the video frames. Please try another video.")


st.markdown("---")
st.subheader('Deepfake Assistant Chatbot')

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
    
if prompt :=st.chat_input("Ask anything about this project or deepfake..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    prompt_lower = prompt.lower()
    if "deepfake" in prompt_lower or "what is" in prompt_lower:
        response = "A deepfake is synthetic media in which a person's likeness in an existing image or video is replaced with someone else's face using artificial intelligence."
    elif "opencv" in prompt_lower or "video" in prompt_lower:
        response = "This app uses OpenCV to capture video frames, detect faces, and crop them for deepfake analysis."
    elif "model" in prompt_lower or "mobilenet" in prompt_lower:
        response = "We used the MobileNetV2 deep learning architecture for image classification and feature extraction in this project."
    elif "streamlit" in prompt_lower or "app" in prompt_lower:
        response = "This web interface is built using Streamlit, backed by an SQLite database to log prediction histories."
    else:
        response = "That's a great question! You can use this application to easily upload and verify whether images or videos are real or fake."

    with st.chat_message("assistant"):
        st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})        
             




    