from flask import Flask, request,make_response, current_app
from flask_failsafe import failsafe
import flask
from flask_cors import CORS, cross_origin
import json
import hashlib
from flaskext.mysql import MySQL
# import ConfigParser
import re
import numpy as np
# from PIL import Image
import base64
from io import StringIO

root = "D:/Vccorp/FingerPrint/cross_browser/flask/"
# config = ConfigParser.ConfigParser()
# config.read(root + 'password.ignore')

mysql = MySQL()
app = Flask(__name__)
# app.config['MYSQL_DATABASE_USER'] = config.get('mysql', 'root')
app.config['MYSQL_DATABASE_USER'] = "root"
# app.config['MYSQL_DATABASE_PASSWORD'] = config.get('mysql', '')
app.config['MYSQL_DATABASE_PASSWORD'] = ""
app.config['MYSQL_DATABASE_DB'] = 'fingerprint'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
CORS(app)
base64_header = "data:image/png;base64,"

mask = []
mac_mask = []

with open(root + "mask.txt", 'r') as f:
    mask = json.loads(f.read())
with open(root + "mac_mask.txt", 'r') as fm:
    mac_mask = json.loads(fm.read())

@app.route("/pictures", methods=['POST'])
def store_pictures():
    image_b64 = request.values['imageBase64']
    # remove the define part of image_b64
    image_b64 = re.sub('^data:image/.+;base64,', '', image_b64)
    # decode image_b64
    image_data = image_b64.decode('base64')
    image_data = StringIO.StringIO(image_data)
    image_PIL = Image.open(image_data)
    image_binary = image_PIL.tobytes().encode('hex')

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO pictures (dataurl) VALUES ('" + image_binary + "')"
    cursor.execute(sql_str)

    sql_str = "SELECT LAST_INSERT_ID()"
    cursor.execute(sql_str)
    ID = cursor.fetchone()
    return str(ID[0])

@app.route('/details', methods=['POST'])
def details():
    print("Get data in details\n")
    res = {}
    ID = request.get_json()["ID"]
    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "SELECT * FROM features WHERE browser_fingerprint = '" + ID +"'"
    cursor.execute(sql_str)
    db.commit()
    row = cursor.fetchone()
    for i in range(len(row)):
        value = row[i]
        name = cursor.description[i][0]
        res[name] = value

    if 'fonts' in res:
        fs = list(res['fonts'])
        for i in range(len(mask)):
            fs[i] = str(int(fs[i]) & mask[i] & mac_mask[i])
        res['fonts'] = ''.join(fs)
    print("Loaded data in details\n")
    return flask.jsonify(res)

@app.route('/features', methods=['POST'])
def features():
    print("Get data in feature\n")
    agent = ""
    accept = ""
    encoding = ""
    language = ""
    IP = ""
    try:
        agent = request.headers.get('User-Agent')
        accept = request.headers.get('Accept')
        encoding = request.headers.get('Accept-Encoding')
        language = request.headers.get('Accept-Language')
        IP = request.remote_addr
    except:
        pass

    feature_list = [
            "agent",
            "accept",
            "encoding",
            "language",
            "langsDetected",
            "resolution",
            "fonts",
            "WebGL", 
            "inc", 
            "gpu", 
            "gpuImgs", 
            "timezone", 
            "plugins", 
            "cookie", 
            "localstorage", 
            "adBlock", 
            "cpu_cores", 
            "canvas_test", 
            "audio"]

    cross_feature_list = [
            "timezone",
            "fonts",
            "langsDetected",
            "audio"
            ]
    
    result = request.get_json()

    single_hash = "single"
    cross_hash = "cross"

    fonts = list(result['fonts'])

    cnt = 0
    for i in range(len(mask)):
        fonts[i] = str(int(fonts[i]) & mask[i] & mac_mask[i])
        if fonts[i] == '1':
            cnt += 1

    result['agent'] = agent
    result['accept'] = accept
    result['encoding'] = encoding
    result['language'] = language
    
    print ("Agent: %s\n" % agent)
           
    feature_str = "IP"
    value_str = "'" + IP + "'"


    for feature in feature_list:
        
        if result[feature] is not "":
            value = result[feature]
        else:
            value = "NULL"

        feature_str += "," + feature
#for gpu imgs
        if feature == "gpuImgs":
            value = ",".join('%s_%s' % (k,v) for k,v in value.items())
        else:
            value = str(value)


        if feature == 'cpu_cores':
            value = int(value)

        if feature == 'langsDetected':
            value = str("".join(value))
            value = value.replace(" u'", "")
            value = value.replace("'", "")
            value = value.replace(",", "_")
            value = value.replace("[", "")
            value = value.replace("]", "")
            value = value[1:]
        
        value_str += ",'" + str(value) + "'"
        #print feature, hash_object.hexdigest()
        
    result['fonts'] = fonts
    for feature in cross_feature_list:
        cross_hash += str(result[feature])
        hash_object = hashlib.md5((str(result[feature])).encode("utf-8"))

    hash_object = hashlib.md5(value_str.encode("utf-8"))
    single_hash = hash_object.hexdigest()

    hash_object = hashlib.md5(cross_hash.encode("utf-8"))
    cross_hash = hash_object.hexdigest()

    feature_str += ',browser_fingerprint,computer_fingerprint_1'
    value_str += ",'" + single_hash + "','" + cross_hash + "'"

    db = mysql.get_db()
    cursor = db.cursor()
    sql_str = "INSERT INTO features (" + feature_str + ") VALUES (" + value_str + ");"
    cursor.execute(sql_str)
    db.commit()

    print (single_hash, cross_hash)
    return flask.jsonify({"single": single_hash, "cross": cross_hash})
