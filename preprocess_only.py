from flask import Flask, request
from flask.templating import render_template

# global var
file_name=""
result_dict = {}

import io
from PIL import Image
import cv2
import numpy as np

def preprocess(n):
    img = f'/home/wonayeonModi/mysite/static/PDFs/{n}.png'
    img_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]])
    img_sharp = cv2.filter2D(img_gray, -1, kernel)
    cv2.imwrite(img, img_sharp)
    img = Image.open(img)
    return img

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploadPDF',methods=['POST'])
def uploadPDF():
    if 'file_upload' not in request.files:
      return "file 업로드 중 error가 발생했습니다."
    else:
      global file_name
      file = request.files['file_upload']
      file.save('/home/wonayeonModi/mysite/static/PDFs/pp.png')
      ppimg = preprocess('pp')  #전처리
      img_byte_arr = io.BytesIO()
      ppimg.save(img_byte_arr, format='png')
      file_name = '/static/PDFs/pp.png'        # 초기화
      #file_name += '/home/wonayeonModi/mysite/static/PDFs/'
      #file_name += str('pp.png')
      return render_template('uploadPDF.html', file_name = file_name)
