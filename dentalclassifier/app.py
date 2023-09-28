
import torch.nn as nn
from flask import Flask, render_template, request, redirect, url_for
import os
from torchvision import transforms
import torch
from PIL import Image
from tanden import SimpleCNN


app = Flask(__name__, template_folder="templates")

# load model
num_classes = 5  # Assuming 5 classes
model = SimpleCNN(num_classes)

checkpoint_path = "dental_classifier.pth"  # Replace with the actual path
model.load_state_dict(torch.load(checkpoint_path))
model.eval()  # Set the model to evaluation mode


# Define a transformation for preprocessing the uploaded image
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    # Add other transformations as needed (e.g., normalization)
])


@app.route('/')
def home():
    # Redirect to the index.html file
    return render_template("index.html")

@app.route("/classify", methods=["POST"])
def classify():
    result = None

    if request.method == "POST":
        if "image" in request.files:
            uploaded_image = request.files["image"]
            if uploaded_image.filename != "":
                # Save the uploaded image
                image_path = os.path.join("static/images", uploaded_image.filename)
                uploaded_image.save(image_path)

                # Preprocess the image
                img = Image.open(image_path)
                img = transform(img)
                print('image transformed')
                img = img.unsqueeze(0)  # Add a batch dimension (single image)

                # Pass the image through the model
                with torch.no_grad():
                    output = model(img)

                # Apply softmax to obtain class probabilities
                softmax = nn.Softmax(dim=1)
                probabilities = softmax(output)
                class_labels = ["gingivitis", "hypodontia", "discoloration", "caries", "calculus"]
                predicted_class = class_labels[torch.argmax(probabilities)]
                confidence_score = torch.max(probabilities).item()

                # Prepare the result message
                result = f"Predicted Class: {predicted_class}, Confidence Score: {confidence_score:.2f}"

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)