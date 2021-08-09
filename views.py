from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
import os
from PIL import Image
import cv2
from matplotlib import pyplot as plt
from pdf2image import convert_from_path
import time


CMD = """
docker run -it --ipc=host -v {path}:/usr/src/app/input_images/ -v /tmp/output:/usr/src/app/inference -v /home/neel/django_etdui/detect2.py:/usr/src/app/detect2.py sampyash/yolov5:airflow_integration python detect2.py --source input_images --weights ./weights/best.pt --conf 0.4 --save-txt --output inference/output 
"""

def index(request):
    return render(request, 'fig_extraction/index.html')


def upload(request):
    context = {}

    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        uploaded=fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(uploaded)
        name_without_ext = "".join(context['url'].split("/")[-1].split(".")[:-1])
        img_name = context['url'].split("/")[-1]
        document_path = os.path.abspath("." + context['url'])

        #PDF to img
        images = convert_from_path(document_path)   # general file path
        cur_time = time.time()
        os.system(f"mkdir {cur_time}")
        paths = []
        for i in range(len(images)):
	        images[i].save(f'{cur_time}/{cur_time}_'+ str(i) +'.jpg', 'JPEG'); paths.append(f"{cur_time}_"+ str(i))

        os.system(
            CMD.format(
                path = os.path.abspath("./" + str(cur_time)),
            )
        )
        for path in paths:
            _time = path.split("_")[0]
            with open(f"/tmp/output/output/{path}.txt") as f:
                data = [ list(map(float, item.strip().split(" ")[1:])) for item in f.read().split("\n") ]
                print(data)
                img = Image.open(os.path.abspath("./" + _time + "/" + path + ".jpg"))
                width, height = img.size
                for item in data:
                    if not (len(item) == 4) : continue
                    x, y, w, h = item

                    img.crop((x,y, w, h)).show()
            


    return render(request, 'fig_extraction/upload.html', context)
