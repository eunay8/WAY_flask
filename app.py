# import os, sys
from flask import Flask, request
from flask.templating import render_template
from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

import easyocr

def ocrcheck(image_path):
  
  reader = easyocr.Reader(['en','ko'], gpu=False) #gpu 사용으로 돌려보기 
  imgPath = image_path
  printData = ""
  
  try:
    result = reader.readtext(imgPath)
    for r in result:
      printData += r[1]
  except FileNotFoundError as e:
    printData += e

  return printData

app = Flask(__name__)
app.debug = True
name=""


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/uploadPDF',methods=['POST'])            #일단 jpg 업로드
def uploadPDF():
    if 'file_upload' not in request.files:
      return "if문 1번"
    else:
      global name
      img = request.files['file_upload']
      img.save('./static/images/' + img.filename)
      img_name = '../static/images/' + str(img.filename)
      name += './static/images/'
      name += str(img.filename)
      return render_template('uploadPDF.html', file_name=img_name)


@app.route('/searchWord', methods=['POST'])           #일단 OCR 결과 출력
def searchWord():
    if request.form['searchStr'] == "검색":
      
        return render_template('searchWord.html', word='검색 스트링을 입력하세요.')
    else: 
        sWord = ocrcheck(name)        #이미지 경로 받아온 걸 매개변수로?
        return render_template('searchWord.html', word=sWord)