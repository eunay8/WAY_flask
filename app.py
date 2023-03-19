import os, sys
from flask import Flask, request
from flask.templating import render_template
# from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
# from . import PDF_to_Text as ptt
import fitz

file_name=""
result_dict = {}

# 여기부터
import io
from PIL import Image
import sys
import os
import easyocr
from pdf2image import convert_from_path

# result_dict = {}

def extractData(pdfPath):
    file = pdfPath
    fitz_pdf = fitz.open(file)
    pdf = 'PDF.pdf'
    all_text = []
    n = len(fitz_pdf)
    
    for i in range(n):
        page = fitz_pdf.load_page(i)
        text = page.get_text("text")
        all_text.append(text)
        for rect in text:
            annot = page.add_redact_annot(rect)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
        fitz_pdf.save(pdf, garbage=3, deflate=True)

        images = convert_from_path(pdf, fmt='png', poppler_path='./poppler/Library/bin')
        reader = easyocr.Reader(['en', 'ko'], gpu=False)

        for i in range(n):
            img_byte_arr = io.BytesIO()
            images[i].save(img_byte_arr, format='png')
            img_byte_arr = img_byte_arr.getvalue()
            result = reader.readtext(img_byte_arr)
            for j in range(len(result)):
                all_text[i] = all_text[i] + result[j][1] 
                #IndexError: list index out of range
        
        global result_dict
        for i in range(len(all_text)):
            result_dict[i] = all_text[i]
            
    return result_dict


def searchWord(searchStr, **dict):
    target = searchStr
    index = -1
    all_result = {} # 전체 결과값
    result_page = [] # 해당 단어가 있는 페이지 리스트
    # global result_dict
    result_dict = {}
    result_dict = dict
    for i in range(len(result_dict)):
        all_result[i] = []
        while True:
            index = result_dict[i].find(target, index + 1)
            if index == -1:
                break
            print('index=%d' % index)
            all_result[i].append(index)

        for i in range(len(all_result.keys())):
            if all_result.get(i):
                result_page.append(i)
                
    return result_page

# 여기까지 

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
      global result_dict
      file = request.files['file_upload']
      file.save('./static/images/' + file.filename)
      # pdf = fitz.open(file)
      # pdf.save('./static/images/' + file.filename)
      file_name += './static/images/'
      file_name += str(file.filename)
      result_dict = extractData(file_name)
    #   test = file.filename
    #   return render_template('uploadPDF.html', file_name = test)
      return render_template('uploadPDF.html', file_name = file_name)


@app.route('/searchWord', methods=['POST'])   
def searchWord():
  if request.form['searchStr'] == "검색":
    return render_template()
  else:
    global file_name
    global result_dict
    page_list = searchWord(result_dict)
    return render_template('searchWord.html', file_name = file_name, page_list = page_list)