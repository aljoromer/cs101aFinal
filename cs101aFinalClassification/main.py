import torch
import torch.nn.functional as F
from torchvision import transforms
from torch import nn
import torchvision.models as model
from torch.autograd import Variable
from PIL import Image as im
import os
import re

'''
Main function: Asks user for a directory of .png files to classify using Final_Model.pt
'''
def main():
    dirPath = input('Path to image directory: ') #Expects a directory
    results = open("results.txt",'w')
    for file in sorted_alphanumeric(os.listdir(dirPath)):
        f = os.path.join(dirPath,file)
        img = im.open(f) 
        results.write('{0},{1}\n'.format(file,predict_image(img)))
    results.close()

#Have to define the Net object to import the model using torch.load
class Net(nn.Module):
    def __init__(self):
        super(Net, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=32, kernel_size=3, stride=1, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, stride=1, padding=1)
        self.fc1 = nn.Linear(64*8*8, 10)

    # x represents our data
    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.pool(x)
        x = F.relu(self.conv2(x))
        x = self.pool(x)
        x = x.reshape(x.shape[0], -1)
        x = self.fc1(x)
        
        return x


#Loading the model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = torch.load('Final_Model.pt')
model.eval()

#To transform images before classification
transform = transforms.Compose([transforms.Grayscale(),
                                transforms.Resize((32,32)),
                                transforms.ToTensor(),
                                transforms.Normalize((0.5,), (0.5,))
                               ])


#Predicts which class the image belongs to (1 through 10)
def predict_image(image):
    image_tensor = transform(image).float()
    image_tensor = image_tensor.unsqueeze_(0)
    input = Variable(image_tensor)
    input = input.to(device)
    output = model(input)
    index = output.data.cpu().numpy().argmax()
    return index + 1

#Sorts alphanumerically. This is for use in main() to sort the images.
def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

if __name__ == '__main__':
    main()