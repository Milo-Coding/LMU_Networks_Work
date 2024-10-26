from flask import Flask, Response
import requests

app = Flask(__name__)

@app.route("/")
def dog_image():
    # Fetch a random dog image from the Dog CEO's Dog API
    response = requests.get("https://dog.ceo/api/breeds/image/random")
    data = response.json()
    
    # Get the image URL from the response JSON
    image_url = data.get("message")
    
    # Fetch the actual image data
    image_response = requests.get(image_url)
    
    # Return the image data as a response
    return Response(image_response.content, mimetype="image/jpeg")