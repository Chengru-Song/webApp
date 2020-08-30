# A Lightweight Image Classification Platform

## Features
- Select from local files to recognize what it is. A mobilenet model is used to predict your input image.
- Using Different methods to accelerate the inference process.
- Multi methods was compared in this lightweight project

<img src="http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4a808845358.png" width=500px>

## Work Flow
When a user decides to use the system for image classification, he/she chooses an image from local filesystem or enter the url of an image. When uploading files, a user could upload multiple files or just one at a time. A user can choose from the methods from the dropdown menu, the choice will be encoded as a parameter in the request url instead of body parameters.

When the image(s) is fed to the system, Fastapi is responsible to handle image classification. Traditionally, the system will call a MobileNet v2 model to analyze the image. The top-1 accuracy and top-5 accuracy is shown as follows, evaluated against 200 images.

![top_1_top_5](http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4a83924893d.png)

The results are tested on a machine running Windows operating system, with a Intel i7-7820x CPU, 64GB memory, RTX 2080 Graphics. The time consumed when running 200 images are shown below. The average time to analyze a single image is 1.344527187347412 s.

![time_consumed](http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4a85d78b61a.png)

After classification, the server deploying Fastapi will reply the client with the names of five classes, whose possibilities ranking from highest to lowest. 

<img src="http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4a882e8a777.png" width=500px>

## Acceleration

Since GPU is a commonly applied approach to speedup training, it is natural to use GPU to speed up the inference process. The simplest approach is to use CUDA to accelerate model inference. We only need to switch it to `model.cuda()` to accelerate the process. The images are tested on the same model without changing any network architecture. Therefore, the top-1 and top-5 accuracy remain the same. See the figure below. 

![accuracy_cuda](http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4a9cbe00209.png)

However, the time consumed on inference is reduced significantly due to the application of CUDA. It achieved a remarkable reduction in consumed time. It only takes 0.037294045686722 s on average to analyze an image. That is 36x times faster than just use CPU to classify an image. The comparison of using CPU and CUDA are shown below. 

![cpu_cuda_comparison](http://showdoc.hypercool.cn:4999/server/../Public/Uploads/2020-08-30/5f4aa104bf7d3.png)