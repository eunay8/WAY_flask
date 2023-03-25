from flask import Flask, request
from flask.templating import render_template
import fitz

# global var
file_name=""
result_dict = {}

# 여기부터
import io
from PIL import Image
import easyocr
from pdf2image import convert_from_path
import cv2
import numpy as np


def preprocess(n):
    img = f'./static/images/page{n}.png'
    img_gray = cv2.imread(img, cv2.IMREAD_GRAYSCALE)
    kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]])
    img_sharp = cv2.filter2D(img_gray, -1, kernel)
    cv2.imwrite(img, img_sharp)
    img = Image.open(img)
    return img


def extractData(pdfPath):
    file = pdfPath
    fitz_pdf = fitz.open(file)
    pdf = 'PDF.pdf'
    all_text = []
    n = len(fitz_pdf)
    
    for i in range(n):
        page = fitz_pdf.load_page(i)
        text = page.get_text("text")
        text = text.lower()                     ##소문자 처리
        text = text.replace(" ","")             ## 공백문자 처리
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
        images[i].save(f'./static/images/page{i}.png')
        ppimg = preprocess(i)
        img_byte_arr = io.BytesIO()
        ppimg.save(img_byte_arr, format='png')
        img_byte_arr = img_byte_arr.getvalue()
        result = []
        result = reader.readtext(img_byte_arr)
        for j in range(len(result)):
            reText = result[j][1]
            reText = reText.lower()             ## 소문자 처리
            reText = reText.replace(" ","")     ## 공백문자 처리
            all_text[i] = all_text[i] + reText + '\n'

    global result_dict
    for i in range(len(all_text)):
        # if (all_text[i]>=65) & (all_text[i]<=90):
        #     all_text[i] = all_text[i] + 32      
        result_dict[i] = all_text[i]
    # result_dict는 전역변수로 저장하고 html 파일에 전달하지 않음 
    # -> 리턴 생략 해도? 될 듯?
            
    return result_dict


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
    #   return render_template('uploadPDF.html', file_name = result_dict)      #딕셔너리()
      return render_template('uploadPDF.html', file_name = file_name)


@app.route('/searchWord', methods=['POST'])   
def searchWord():
    global file_name
    if request.form['searchStr'] == "": 
        page_list = []
    else:
        seStr = ""
        seStr = seStr +  request.form['searchStr']
        seStr = seStr.lower()
        seStr = seStr.replace(" ", "")
        page_list = searchData(seStr)
        print(type(page_list[0]))
        # file_name을 애초에 첫번째 index 페이지로 연결해서 변수 전달
        print(type(file_name))
        
    return render_template('searchWord.html', file_name = file_name, page_list = page_list)
