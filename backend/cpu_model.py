import torch
from PIL import Image
from torchvision import transforms
import time

class Model(object):
    def __init__(self):
        super().__init__()
        print("Initialize models")

    def predict(self, file):
        pass

class MobileNet(Model):
    def __init__(self):
        super().__init__()
        self.__model = torch.hub.load('pytorch/vision:v0.6.0', 'mobilenet_v2', pretrained=True)
        self.__model.eval()

    def predict(self, file):
        input_image = Image.open(file)

        preprocess = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        input_tensor = preprocess(input_image)
        input_batch = input_tensor.unsqueeze(0) # create a mini-batch as expected by the model

        with open('classes.txt') as f:
            labels = [line.strip() for line in f.readlines()]


        with torch.no_grad():
            output = self.__model(input_batch)
        
        _, index = torch.max(output, 1)
        percentage = torch.nn.functional.softmax(output, dim=1)[0] * 100

        _, indices = torch.sort(output, descending=True)
        return [(labels[idx], percentage[idx].item()) for idx in indices[0][:5]]