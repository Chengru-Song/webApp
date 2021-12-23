# A Lightweight Image Classification Platform

## Project Structure


```
.
├── CHANGELOG.md
├── ISSUE_TEMPLATE.md
├── README.md
├── babel.config.js
├── backend
│   ├── TensorRT.ipynb
│   ├── __pycache__
│   ├── classes.txt             // Imagenet 1000 classes
│   ├── config.py               // baseURL and worker URLs
│   ├── cpu_model.py            // Model use CPU
│   ├── dataset.py  
│   ├── env.yml                 // Anaconda enviroment
│   ├── evaluation_results      // Evaluation Result
│   ├── gpu_models.py           // Model use cuda and tensorRT
│   ├── main.py                 // FastApi entry
│   ├── meta.bin
│   ├── mobilenet.onnx          // ONNX model, converted from pytorch mobilenet
│   ├── mobilenet_v2            // pytorch mobilenet model
│   ├── mobilenetv2-7.onnx
│   ├── newTest.ipynb           // All test and simulation results are generated from this file
│   ├── result.csv
│   ├── result2.csv
│   ├── testMobileNet.ipynb
│   ├── test_dataset.txt
│   ├── testimages              // Some hand label images for classification
│   └── webapp.yml
├── frontend
├── package-lock.json
├── package.json
├── public
│   ├── favicon.ico
│   ├── favicon.png
│   ├── img
│   └── index.html
├── src
│   ├── App.vue
│   ├── api
│   ├── assets
│   ├── components
│   ├── directives
│   ├── layout
│   ├── main.js
│   ├── plugins
│   ├── registerServiceWorker.js
│   ├── router.js
│   ├── starterRouter.js
│   ├── store
│   ├── utils
│   └── views
├── vue.config.js
└── yarn.lock
```

## Features
- Select from local files to recognize what it is. A mobilenet model is used to predict your input image.
- Using Different methods to accelerate the inference process.
- Multi methods was compared in this lightweight project

<img src="https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/after_prediction.png" width=500px>

## Work Flow
When a user decides to use the system for image classification, he/she chooses an image from local filesystem or enter the url of an image. When uploading files, a user could upload multiple files or just one at a time. A user can choose from the methods from the dropdown menu, the choice will be encoded as a parameter in the request url instead of body parameters.

When the image(s) is fed to the system, Fastapi is responsible to handle image classification. Traditionally, the system will call a MobileNet v2 model to analyze the image. The top-1 accuracy and top-5 accuracy is shown as follows, evaluated against 200 images.

![top_1_top_5](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/top_1%20top_5.png)

The results are tested on a machine running Windows operating system, with a Intel i7-7820x CPU, 64GB memory, RTX 2080 Graphics. The time consumed when running 200 images are shown below. The average time to analyze a single image is 1.344527187347412 s.

![time_consumed](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/time_collapsed.png)

After classification, the server deploying Fastapi will reply the client with the names of five classes, whose possibilities ranking from highest to lowest. 


## Acceleration

### Accelerate with Pytorch Cuda

Since GPU is a commonly applied approach to speedup training, it is natural to use GPU to speed up the inference process. The simplest approach is to use CUDA to accelerate model inference. We only need to switch it to `model.cuda()` to accelerate the process. The images are tested on the same model without changing any network architecture. Therefore, the top-1 and top-5 accuracy remain the same. See the figure below. 

![accuracy_cuda](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/accuracy_cuda.png)

However, the time consumed on inference is reduced significantly due to the application of CUDA. It achieved a remarkable reduction in consumed time. It only takes 0.037294045686722 s on average to analyze an image. That is 36x times faster than just use CPU to classify an image. The comparison of using CPU and CUDA are shown below. 

![cpu_cuda_comparison](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/cuda_cpu_comparison.png)

### Accelarate with TensorRT

The pytorch model running with cuda gains a significant improvement on the image classification time. However, a recent approach is deploying TensorRT on the server machine to accelerate the inference process. As demonstrated on TensorRT website, it can perform up to 40x faster than CPU only systems. Owing to Nvidia's parallel programming model, it provides INT8 and FP16 optimizations for production deployments of deep learning inference applications such as video streaming, speech recognition, recommendation and natural language processing. So I deployed it on the same machine to evaluate this approach. Fortunately, the results are quite satisfying. The average time spent to analyze an image is 0.0008525 s.

When comparing with pytorch's cuda version:

![torch&TensorRT](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/torch%26tensorRT.png)

When comparing them altogether, we got the following result.

![compareAll](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/compareAll.png)

### Accelerate with distributed computing

Lightweight models are usually used in video analysis or edge nodes whose computing power are constrained. The aforementioned methods are all accelerating the inference locally using GPU. Therefore, if edge nodes could be leveraged to analyze images in a distributed manner, it could gain significantly in performence. As a result, I offer an option for users to choose whether they want to use distributed devices for bulk inference. If selected, the browser will automatically split the input images evenly and send the files to active workers asynchronously. 

We tested the time spent on different batch sizes of input images. In our test enviroment, workers are set to 3 and the batch size is ranging from 5-150 images. The results are quite satisfying. 

![single&multiple](https://github.com/Chengru-Song/webApp/blob/master/backend/evaluation_results/single%26multiple.png)

## Summary

This project is a lightweight image classification web application that returns a possible catogory of an image. We used three methods to accelerate the inference process. The standard time consumed is using a MobileNetv2 model from pytorch to analyze an image on CPU. When enabling CUDA with RTX 2080, the average time consumed to analyze an image is 36x time faster than running on CPU. After applying TensorRT on a MobileNetv2 converted onnx model, the average time spent to analyze an image is 43x time faster than running on pytorch cuda. In addition, we applied distributed inference on images when inputing multiple files at a time. The result is related to the number of workers and network latency which, if properly adjusted, will produce further reduction on the time spent to analyze an image.

## Future Work

- Unravel the relationship among network latency, network speed and the number of workers. 
