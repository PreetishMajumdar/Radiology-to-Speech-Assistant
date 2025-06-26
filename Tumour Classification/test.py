import tensorflow as tf
import numpy as np
import cv2
import os

# === CONFIG ===
MODEL_PATH = "D:\VS Code Projects\Radiology-to-Speech-Assistant\Tumour Classification\models\scan_type_classifier_aspect_safe.keras"  # or .keras if you're using the newer format
IMG_SIZE = (224, 224)
CLASS_NAMES = ['Abdomen Ultrasound', 'Brain MRI', 'Breast Ultrasound']  # Replace with your class names

# === Load Model ===
model = tf.keras.models.load_model(MODEL_PATH)

# === Preprocessing Function (Aspect Ratio Safe) ===
def preprocess_image(image_path):
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ File not found: {image_path}")

    image = cv2.imread(image_path)
    if image is None:
        raise ValueError(f"❌ Could not read image: {image_path}")

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = tf.convert_to_tensor(image, dtype=tf.float32)
    image = tf.image.resize_with_pad(image, IMG_SIZE[0], IMG_SIZE[1])
    image = image / 255.0
    return np.expand_dims(image, axis=0)

# === Input from User ===
image_path = input("📂 Enter the full image path of the scan (e.g., D:/scans/scan1.jpg): ").strip()

try:
    input_tensor = preprocess_image(image_path)
    prediction = model.predict(input_tensor)
    predicted_class = CLASS_NAMES[np.argmax(prediction)]

    print(f"✅ Predicted Scan Type: {predicted_class}")
except Exception as e:
    print(e)

