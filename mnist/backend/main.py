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
import os

app = Flask(__name__)
app.config["IMAGE_UPLOADS"] = "./Upload/"

def getEnvOrDefault(key, fallback):
    value = os.getenv(key, "None")
    if value == "None":
        return fallback
    return value
    
PORT = getEnvOrDefault("PORT", 9001)

class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(1, 32, 3, 1)
        self.conv2 = nn.Conv2d(32, 64, 3, 1)
        self.dropout1 = nn.Dropout(0.25)
        self.dropout2 = nn.Dropout(0.5)
        self.fc1 = nn.Linear(9216, 128)
        self.fc2 = nn.Linear(128, 10)

    def forward(self, x):
        x = self.conv1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = F.relu(x)
        x = F.max_pool2d(x, 2)
        x = self.dropout1(x)
        x = torch.flatten(x, 1)
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout2(x)
        x = self.fc2(x)
        output = F.log_softmax(x, dim=1)
        return output


def train(args, model, device, train_loader, optimizer, epoch):
    model.train()
    for batch_idx, (data, target) in enumerate(train_loader):
        data, target = data.to(device), target.to(device)
        optimizer.zero_grad()
        output = model(data)
        loss = F.nll_loss(output, target)
        loss.backward()
        optimizer.step()
        if batch_idx % args.log_interval == 0:
            print('Train Epoch: {} [{}/{} ({:.0f}%)]\tLoss: {:.6f}'.format(
                epoch, batch_idx * len(data), len(train_loader.dataset),
                100. * batch_idx / len(train_loader), loss.item()))
            if args.dry_run:
                break


def transformer(input):
    transform=transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
        ])
    return transform(input)

def process(input):
    input = transformer(input)
    return input.unsqueeze(0)

def inference(input):
    model = Net()
    model.load_state_dict(torch.load('./mnt/mnist_cnn.pt', map_location=torch.device('cpu')))
    model.eval()
    output = model(input).squeeze().argmax().item()
    #print(output)
    return output

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/infer', methods=['POST'])
def get_dynamic_inference():
    res = {}
    image = request.files["image"]
    if not image:
        res['status'] = 'image missing'
    else:
        res['status'] = 'success'
        #image=file
        image.save(os.path.join(app.config["IMAGE_UPLOADS"], image.filename)) 
        image = Image.open(image.stream)
        output = inference(process(image))
        res['result'] = output
    return json.dumps(res)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=True)