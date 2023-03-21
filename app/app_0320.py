# import os, sys
from flask import Flask, request
from flask.templating import render_template
# from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
# from . import PDF_to_Text as ptt
import fitz

# global var
file_name=""
result_dict = {}

# 여기부터
import io
from PIL import Image
import sys
import os
import easyocr
from pdf2image import convert_from_path




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
        #text 추출
        
        for rect in text:
            annot = page.add_redact_annot(rect)
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE)
    fitz_pdf.save(pdf, garbage=3, deflate=True)
    #text 삭제

    images = convert_from_path(pdf, fmt='png', poppler_path='./poppler/Library/bin')
    #pdf2image
    reader = easyocr.Reader(['en', 'ko'], gpu=True)     # False

    for i in range(n):
        img_byte_arr = io.BytesIO()
        images[i].save(img_byte_arr, format='png')
        img_byte_arr = img_byte_arr.getvalue()
        result = []
        result = reader.readtext(img_byte_arr)
        for j in range(len(result)):
            all_text[i] = all_text[i] + result[j][1]
            # IndexError: list index out of range

    global result_dict
    for i in range(len(all_text)):
        result_dict[i] = all_text[i]
    # result_dict는 전역변수로 저장하고 html 파일에 전달하지 않음
    
    # img_byte_arr = io.BytesIO()
    # images[0].save(img_byte_arr, format='png')
    # img_byte_arr = img_byte_arr.getvalue()
    # result = []
    # result = reader.readtext(img_byte_arr)
    # for j in range(len(result)):
    #     all_text[0] = all_text[0] + result[j][1]
            
    return result_dict
    # return type(result) #len(result)


def searchData(searchStr):
    target = searchStr
    index = -1
    all_result = {} # 전체 결과값
    page_list = [] # 해당 단어가 있는 페이지 리스트
    global result_dict
    # result_dict = {}
    # result_dict = dict    #global var 사용하지 않고 extract의 리턴값, search의 매개변수로 전달 (미지수)
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
            page_list.append(i)
                
    return page_list      # search 문자열이 있는 페이지 list
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
      file.save('./static/PDFs/' + file.filename)
      file_name = ''        # 초기화
      file_name += './static/PDFs/'
      file_name += str(file.filename)
      result_dict = extractData(file_name)
    #   test = extractData(file_name)
    #   return render_template('uploadPDF.html', file_name = test)
      return render_template('uploadPDF.html', file_name = file_name)


@app.route('/searchWord', methods=['POST'])   
def searchWord():
    global file_name
    if request.form['searchStr'] == "": 
        page_list = []
    else:
        seStr = ""
        seStr = seStr +  request.form['searchStr']
        page_list = searchData(seStr)
        
    return render_template('searchWord.html', file_name = file_name, page_list = page_list)
