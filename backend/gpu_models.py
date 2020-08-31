import torch
from PIL import Image
from torchvision import transforms

import tensorrt as trt
import numpy as np
import pycuda.autoinit
import pycuda.driver as cuda 
import time
import keras
from keras.preprocessing.image import ImageDataGenerator
ONNX_FILE_PATH = 'mobilenetv2-7.onnx'
input_size = 32

class Model(object):
    def __init__(self):
        super().__init__()
        print("Initialize models")

    def predict(self, file):
        pass

class MobileNetCuda(Model):
    def __init__(self):
        super().__init__()
        self._model = torch.hub.load('pytorch/vision:v0.6.0', 'mobilenet_v2', pretrained=True)
        self._model.eval()
        self._model.cuda()
        
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
            output = self._model(input_batch)
        
        _, index = torch.max(output, 1)
        percentage = torch.nn.functional.softmax(output, dim=1)[0] * 100

        _, indices = torch.sort(output, descending=True)
        return [(labels[idx], percentage[idx].item()) for idx in indices[0][:5]]


class MobileNetTensorRT(Model):
    def __init__(self):
        super().__init__()
        self.__TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
        self.__engine = self._build_engine(ONNX_FILE_PATH)
        self.__context = self.__engine.create_execution_context()
    
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


        host_input = np.array(input_batch.numpy(), dtype=np.float32, order='C')
        
        host_output, out_shape = self.__inference(host_input)

        output = torch.Tensor(host_output).reshape(self.__engine.max_batch_size, out_shape)
        _, index = torch.max(output, 1)
        percentage = torch.nn.functional.softmax(output, dim=1)[0] * 100

        _, indices = torch.sort(output, descending=True)
        return [(labels[idx], percentage[idx].item()) for idx in indices[0][:5]]
    
    def __build_engine(self, model_path):
        with trt.Builder(self.__TRT_LOGGER) as builder, \
            builder.create_network() as network, \
            trt.OnnxParser(network, self.__TRT_LOGGER) as parser: 
            builder.max_workspace_size = 1<<20
            builder.max_batch_size = 1
            with open(model_path, "rb") as f:
                parser.parse(f.read())
            engine = builder.build_cuda_engine(network)
            return engine
    
    def __alloc_buf(self):
        # host cpu mem
        h_in_size = trt.volume(self.__engine.get_binding_shape(0))
        h_out_size = trt.volume(self.__engine.get_binding_shape(1))
        h_in_dtype = trt.nptype(self.__engine.get_binding_dtype(0))
        h_out_dtype = trt.nptype(self.__engine.get_binding_dtype(1))
        in_cpu = cuda.pagelocked_empty(h_in_size, h_in_dtype)
        out_cpu = cuda.pagelocked_empty(h_out_size, h_out_dtype)
        # allocate gpu mem
        in_gpu = cuda.mem_alloc(in_cpu.nbytes)
        out_gpu = cuda.mem_alloc(out_cpu.nbytes)
        stream = cuda.Stream()
        return in_cpu, out_cpu, in_gpu, out_gpu, stream, h_out_size

    def __inference(self, inputs):
        # async version
        # with engine.create_execution_context() as context:  # cost time to initialize
        # cuda.memcpy_htod_async(in_gpu, inputs, stream)
        # context.execute_async(1, [int(in_gpu), int(out_gpu)], stream.handle, None)
        # cuda.memcpy_dtoh_async(out_cpu, out_gpu, stream)
        # stream.synchronize()

        # sync version
        in_gpu, out_cpu, in_gpu, out_gpu, stream, out_shape = self.__alloc_buf()
        cuda.memcpy_htod(in_gpu, inputs)
        self.__context.execute(1, [int(in_gpu), int(out_gpu)])
        cuda.memcpy_dtoh(out_cpu, out_gpu)
        return out_cpu, out_shape
    
