from __future__ import print_function
import argparse
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torchvision import datasets, transforms
from torch.optim.lr_scheduler import StepLR
from flask import Flask, redirect, jsonify, request, url_for, render_template, flash, json
from PIL import Image
import requests
import os

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "./Upload/"

def getEnvOrDefault(key, fallback):
    value = os.getenv(key, "None")
    if value == "None":
        return fallback
    return value
    
PORT = getEnvOrDefault("PORT", 9002)
BackendServiceURL = getEnvOrDefault("COUNTING_SERVICE_URL", "http://localhost:9001")

def get_dynamic_inference(file):
    res = {}
    if not file:
        res['status'] = 'image missing'
    else:
        res['status'] = 'success'
        #image = Image.open(file.stream)
        #image=file
        output = inference(file).json()
        res['result'] = output['result']
    return res

@app.route('/upload-image', methods=['GET', 'POST'])
def upload_image():
    if request.method == "POST":
        if request.files:
            image = request.files["image"]
            image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename))
            status = get_dynamic_inference(image)
            return render_template("upload_image.html", uploaded_image=image.filename, inf_status=status)
    return render_template("upload_image.html")


@app.route('/uploads/<filename>')
def send_uploaded_file(filename=''):
    from flask import send_from_directory
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


def inference(input):
    ## Write code to connect with infer service
    img = open(f"./Upload/{input.filename}", 'rb').read()
    response = requests.post(url=f"{BackendServiceURL}/infer", files={'image': img})
    #response = requests.post(url="http://0.0.0.0:9001/infer",data=paras)
    # app.logger.info(response)
    return response


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)