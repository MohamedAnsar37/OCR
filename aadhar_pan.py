import easyocr
import re
import cv2
import base64
import numpy as np
from flask import Flask, request
from flask_restful import Resource, Api
import datetime
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
api = Api(app)



class Kyc(Resource):
    def post(self):
        if request.method == 'POST':
            f = request.files['file']
            f.save(os.path.join("imagesfile", secure_filename(f.filename)))
            img = cv2.imread((os.path.join("imagesfile", secure_filename(f.filename))))
            # img = request.json
            # date_time= datetime.datetime.now().strftime("%Y_%m_%d-%I.%M.%S_%p")
            # with open('imagesbase64//{}.jpg'.format(date_time), "wb") as fh:
            #     fh.write(base64.decodebytes(bytes(img['image_base64'], 'utf-8')))
            #
            # im_bytes = base64.b64decode(img['image_base64'])
            # im_arr = np.frombuffer(im_bytes, dtype=np.uint8)
            # img= cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)


        reader = easyocr.Reader(['en'], gpu=True)
        result=reader.readtext(img)


        words = ""
        wordslist=[]
        newwords=[]
        for i, word in enumerate(result):
            print(word[1],round(word[2],2))
            words = words + word[1]
            wordslist.append(word[1])
            if word[2]> 0.40:     # cpu =0.40, gpu=0.30
                newwords.append(word[1])
        print(newwords)


        if ("INCOME" in words.upper()) or ("TAX" in words.upper()) or ("DEPARTMENT" in words.upper()) or ("DEPART" in words.upper()):
            doc = "Pan card"
            if "Father" not in words:
                for n in range(0,len(newwords)-1):
                    if "INDIA" in newwords[n]:
                        name = newwords[n+1]
                        fathers_name =newwords[n+2]
                        break
                for i,word in enumerate(result):
                    # if "INDIA" in word[1]:
                    #     name = result[i+1][1]
                    #     fathers_name = result[i+2][1]
                    panmatch = re.match("[A-Z][A-Z][A-Z][A-Z][A-Z][0-9 BGIOS][0-9 BGIOS][0-9 BGIOS][0-9 BGIOS][A-Z]", word[1])
                    if panmatch:
                        pan=word[1]
                    datematch = re.match("[0-9][0-9][-/][0-9][0-9][-/][0-9][0-9][0-9][0-9]",word[1])
                    if datematch:
                        dob=word[1]
                try:
                    new_pan = ''
                    for n in range(0, 5):
                        new_pan = new_pan + pan[n]
                    for n in range(5,9):
                        if pan[n] in ['0','1','2','3','4','5','6','7','8','9']:
                            new_pan = new_pan + pan[n]
                        elif pan[n] == 'B':
                            new_pan = new_pan + '8'
                        elif pan[n] == 'G':
                            new_pan = new_pan + '6'
                        elif pan[n] == 'O':
                            new_pan = new_pan + '0'
                        elif pan[n] == 'S':
                            new_pan = new_pan + '5'
                        elif pan[n] == 'I':
                            new_pan = new_pan + '1'
                    new_pan = new_pan + pan[9]
                except:
                    new_pan=0
                finally:
                    if new_pan!=0 and re.match("[A-Z][A-Z][A-Z][^P][A-Z][0-9][0-9][0-9][0-9][A-Z]",new_pan):
                        for n in range(0, len(wordslist)-1):
                            if "INDIA" in wordslist[n]:
                                if "INDIA" in wordslist[n+1]:
                                    name = wordslist[n+1]
                                break
                        return {"doc_type": doc, "name" : name, "doc_id" : new_pan, "dob":dob}
                    try:
                        return {"doc_type": doc, "name" : name, "father": fathers_name, "doc_id" : new_pan, "dob":dob}
                    except UnboundLocalError as ue:
                        var_name = re.findall(r"'([^']*)'", str(ue))[0]
                        if var_name == "dob":
                            dob = 0
                            return {"doc_type": doc, "name" : name, "father": fathers_name, "doc_id" : new_pan, "dob":dob}


            else:
                names=[]
                for i,word in enumerate(result):
                    if "Name" in word[1]:
                        names.append(result[i+1][1])
                    panmatch = re.match("[A-Z][A-Z][A-Z][A-Z][A-Z][0-9 BGIOS][0-9 BGIOS][0-9 BGIOS][0-9 BGIOS][A-Z]",word[1])
                    if panmatch:
                        pan=word[1]
                    datematch = re.match("[0-9][0-9][-/][0-9][0-9][-/][0-9][0-9][0-9][0-9]",word[1])
                    if datematch:
                        dob=word[1]
                try:
                    new_pan = ''
                    for n in range(0, 5):
                        new_pan = new_pan + pan[n]
                    for n in range(5,9):
                        if pan[n] in ['0','1','2','3','4','5','6','7','8','9']:
                            new_pan = new_pan + pan[n]
                        elif pan[n] == 'B':
                            new_pan = new_pan + '8'
                        elif pan[n] == 'G':
                            new_pan = new_pan + '6'
                        elif pan[n] == 'O':
                            new_pan = new_pan + '0'
                        elif pan[n] == 'S':
                            new_pan = new_pan + '5'
                        elif pan[n] == 'I':
                            new_pan = new_pan + '1'
                    new_pan = new_pan + pan[9]
                except:
                    new_pan = 0
                finally:
                    if len(names)<2:
                        names=[0, 0]
                    try:
                        return {"doc_type": doc, "name" : names[0], "father": names[1], "doc_id" : new_pan, "dob":dob}
                    except UnboundLocalError as ue:
                        var_name = re.findall(r"'([^']*)'", str(ue))[0]
                        if var_name == "dob":
                            dob = 0
                            return {"doc_type": doc, "name" : names[0], "father": names[1], "doc_id" : new_pan, "dob":dob}
        else:
            doc = "Aadhaar"
            aadhaar1 = 0

            for i,word in enumerate(result):

                aadhaar_match1 =re.match(r'^\d{4}\s*\d{4}\s*\d{4}$',word[1])
                if aadhaar_match1:
                    aadhaar1 = word[1]
                if  re.match("[0-9][0-9][0-9][0-9]", word[1]):
                    aadhaar2 = result[i-2][1] + result[i-1][1] + result[i][1]
                dob = re.findall("[0-9][0-9][-/][0-9][0-9][-/][0-9][0-9][0-9][0-9]",word[1])
                if dob:
                    date_of_birth = dob[0]
                if ("Male" in word[1]) or ("MALE" in word[1]):
                    gender="Male"
                if ("Female" in word[1]) or ("FEMALE" in word[1]):
                    gender="Female"

            for n in range((len(newwords)-1),-1,-1):
                if "India" in newwords[n] or "INDIA" in newwords[n] or "india" in newwords[n]:
                    name = newwords[n+1]
                    break

            if aadhaar1 == 0:
                aadhaar=aadhaar2
            else:
                aadhaar=aadhaar1
            aadhaar= re.sub(r'[^0-9]','', aadhaar)
            aadhaar= aadhaar[:12]
            if aadhaar.isnumeric()==False:
                aadhaar = 0

            if ("Year" in words) or ("Birth" in words):
                for n in range(0, len(wordslist)):
                    if "Year" in wordslist[n] or "Birth" in wordslist[n]:
                        date_of_birth= wordslist[n+1]
                        break
            # if aadhaar != 0:
            #     if  re.match(r'^\d{12}$',aadhaar) == False:
            #         aadhaar=0


            # if "India" not in words:
            #     if "INDIA" not in words:
            #         name = 0
            try:
                print(date_of_birth)
            except:
                date_of_birth=0
            try:
                print(name)
            except:
                name=0
            try:
                print(gender)
            except:
                gender=0
            # try:
            return {"doc_type": doc,  "dob" : date_of_birth,  "doc_id" : aadhaar, "name" : name, "gender":gender}
            # except UnboundLocalError as ue:
            #     var_name = re.findall(r"'([^']*)'", str(ue))[0]
            #     if var_name == "date_of_birth":
            #         date_of_birth = 0
            #         return {"doc_type": doc,  "dob" : date_of_birth, "Name" : name, "doc_id" : aadhaar, "Gender":gender}








api.add_resource(Kyc,'/')
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5003)
