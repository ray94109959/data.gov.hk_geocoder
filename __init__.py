import sys
import chardet
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response,send_from_directory
from flask.helpers import send_file
from werkzeug.utils import secure_filename
import pandas as pd
import pathlib
import zipfile
from os.path import basename
import csv
from os import listdir
import os
from uuid import uuid4
import datetime

sys.path.append('/bd-ogcdp/tools/geo_coding_tool/validator')
# import validate_data_json #
import geocoder

app = Flask(__name__)
# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024
app.secret_key = '123456789'
# app.run(debug=True) 

# filehex = uuid4().hex
# app.config['UPLOAD_FOLDER']  = os.path.join('/bd-ogcdp/tools/geo_coding_tool/validator/csvupload', filehex)
# if not os.path.exists(app.config['UPLOAD_FOLDER']):
#     os.makedirs(app.config['UPLOAD_FOLDER'])
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

def changehex(): #make/change file directory
    filehex = uuid4().hex
    changehex.filehex = filehex
    app.config['UPLOAD_FOLDER']  = os.path.join('/bd-ogcdp/tools/geo_coding_tool/validator/csvupload', filehex)
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])

def timenow():
    d1 = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
    return d1

if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

def getdata(csvdata, addresscolumn): #get data from ADI Tool
    # colname = "Address Name"
    shape = csvdata.shape
    error100row = ''
    nocolname = ''
    # print('shape', shape)
    numberofmaxrow = 500
    getdata.numberofmaxrow = numberofmaxrow
    if shape[0] > numberofmaxrow:
        # print('csv have more than xxx row')
        error100row = 'More than 200 row'
        getdata.error100row = error100row
        return error100row
    else:
        getdata.error100row = error100row
        try:
            getdata.nocolname = nocolname
            colname = addresscolumn
            addressdata = csvdata[colname].tolist()
            logfilename = ''.join([front.urlfilename, '-logfile.csv'])
            logsavepath = os.path.join(app.config["UPLOAD_FOLDER"], logfilename)
            csvheader = ["ID","Address Name", "Score", "Remarks", "Latitude", "Longitude", "Geoaddress","English Address Returned by ALS", "Chinese Address Returned by ALS"]
            with open(logsavepath, 'w') as blank:
                blankwriter = csv.writer(blank, delimiter=',')
                blankwriter.writerow(csvheader)

            geocoder.findaddress(addressdata, logsavepath)
            csvdata["ALS Latitude"] = geocoder.latlist
            csvdata["ALS Longitude"] = geocoder.lnglist
            return csvdata
        except:
            nocolname = 'Column Name Not Found'
            getdata.nocolname = nocolname
            return nocolname

def allowed_file(filename): #Allowed file type
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def front():
    if request.method == 'GET': #Get tool website
        print('1000')
        auth_info = 'Internet'
        path_prefix = ''
        return render_template('page.html',
                            auth_info=auth_info,
                            submitbuttondisplay = 'show',
                            datacsvcsv = '',
                            path_prefix=path_prefix,
                            csvdownload = "",
                            submitbuttonpressed = '',
                            message = '')

    if request.method == 'POST': #Post, after clicking submit button
        print('1001')
        changehex()
        # print(changehex.filehex)
        # printchangehex = changehex.filehex
        auth_info = 'Internet'
        path_prefix = ''
        # autocrlf = false
        # if not request:
        #     return render_template('page.html',
        #                         submitbuttondisplay = 'show',
        #                         submitbuttonpressed = '',
        #                         datacsvcsv = '',
        #                         auth_info=auth_info,
        #                         path_prefix=path_prefix,
        #                         csvdownload = "",
        #                         message_failed = 'Please upload a csv file')
        data_file = request.files['data_file'] #get uploaded file by user
        print('1002')
        addresscol = request.form['addresscol']#get address column name by user
        print('1003')
        option = request.form['radioa']
        # print(type(data_file))
        
        if data_file.filename=='': #Check for upload file
            print('1004')
            return render_template('page.html',
                                submitbuttondisplay = 'show',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                submitbuttonpressed = '',
                                message_failed = 'Upload file not found',
                                datacsvcsv = ''
                                )
        
        if addresscol=='': #Check for Address Column Name
            print('1004')
            return render_template('page.html',
                                submitbuttondisplay = 'show',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                submitbuttonpressed = '',
                                datacsvcsv = '',
                                message_failed = 'Please enter Address Field Name, it cannot be empty.'
                                )
        

        if allowed_file(data_file.filename):
            try:
                print('1004')                           #Success
                data_file.seek(0, os.SEEK_END)
                data_file_length = data_file.tell()
                # print(data_file_length)
                data_file.seek(0, 0)
                if data_file_length > (2*1028*1028):   #Check for file size
                    print('1005')
                    return render_template('page.html',
                                    submitbuttondisplay = 'show',
                                    auth_info=auth_info,
                                    path_prefix=path_prefix,
                                    csvdownload = "",
                                    submitbuttonpressed = '',
                                    message_failed = 'Upload file too large',
                                    datacsvcsv = ''
                                    )
                filename = secure_filename(data_file.filename)
                urlfilename = filename[:-4]
                # urlfilenamet = filename[:-4]
                # urlfilenametr = urlfilenamet.replace(' ', '_')
                # urlfilename = urlfilenametr.translate({ord(c): "" for c in "!@#$%^&*()[]{};:,./<>?\|`~-=+"})
                front.urlfilename = urlfilename
                logfilename = ''.join([urlfilename, '-logfile.csv'])
                front.logfilename = logfilename
                print('urlfilename: ',urlfilename)
                print('1005')
                logsavepath = os.path.join(app.config["UPLOAD_FOLDER"], logfilename)
                front.logsavepath = logsavepath
                front.filename = filename
                d1 = timenow()
                front.addresscol = addresscol
                
                # filename = front.filename
                # print(filename[-4:])
                if filename[-4:] == 'xlsx':          #Check for file type and save to directory
                    print('1006')
                    excelfilename = ''.join([urlfilename, '.csv'])
                    data_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    datacsv = pd.read_excel(os.path.join(app.config["UPLOAD_FOLDER"], filename), index_col=None, engine='openpyxl') #pip3 install openpyxl, xlrd
                    editedfilename = ''.join(['edit_',excelfilename])
                elif filename[-4:] == '.xls':
                    print('1006')
                    excelfilename = ''.join([urlfilename, '.csv'])
                    data_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    datacsv = pd.read_excel(os.path.join(app.config["UPLOAD_FOLDER"], filename), index_col=None) 
                    editedfilename = ''.join(['edit_',excelfilename])
                elif filename[-4:] == '.csv':
                    # print('iscsv')
                    print('1006')
                    data_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                    try:
                        print('1006a')
                        # data_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        datacsv = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename), encoding='utf-8-sig')
                        editedfilename = ''.join(['edit_',filename])
                    except:
                        print('1006a')
                        # print(data_file)
                        # data_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
                        datacsv1 = open(os.path.join(app.config["UPLOAD_FOLDER"], filename), 'rb').read()
                        uniencoding = chardet.detect(datacsv1).get('encoding')
                        print(uniencoding)
                        try:
                            print('1006b')
                            datacsv = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename), encoding=uniencoding)  #Check for encoding
                        except:
                            print('1006b')
                            datacsv = pd.read_csv(os.path.join(app.config["UPLOAD_FOLDER"], filename), encoding=uniencoding, delimiter='\t')
                        editedfilename = ''.join(['edited-',filename])

                
                getdata(datacsv, front.addresscol) #Get data from getdata()
                # print(datacsv)
                if getdata.error100row != '':
                    print('1011A')
                    return render_template('page.html',
                                submitbuttondisplay = 'show',
                                submitbuttonpressed = '',
                                datacsvcsv = '',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                message_failed = 'Uploaded file have more than {maxrow} rows.'.format(maxrow=getdata.numberofmaxrow))
                else:
                    print('1011')
                    if getdata.nocolname != '':
                        return render_template('page.html',
                                submitbuttondisplay = 'show',
                                submitbuttonpressed = '',
                                datacsvcsv = '',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                message_failed = 'Address Column Not Found')
                    else:
                        datacsv.to_csv(os.path.join(app.config["UPLOAD_FOLDER"], editedfilename),index=False)
                        print(editedfilename)
                        front.editedfilename = editedfilename
                        with open(os.path.join(app.config["UPLOAD_FOLDER"], editedfilename)) as csv_file:
                            csv_reader = csv.reader(csv_file, delimiter=',')
                            csv_reader = list(csv_reader)
                        print('1012')
                        with open(os.path.join(app.config["UPLOAD_FOLDER"], logfilename)) as csv_file:
                            log_reader = csv.reader(csv_file, delimiter=',')
                            log_reader = list(log_reader)
                        
                        dir_name = os.path.join(app.config["UPLOAD_FOLDER"],'{originalfilename}.zip').format(originalfilename = urlfilename)


                        with zipfile.ZipFile(dir_name, 'w') as zipObj2:
                            zipObj2.write(os.path.join(app.config["UPLOAD_FOLDER"], '{csvfilename}'.format(csvfilename = editedfilename)), basename(os.path.join(app.config["UPLOAD_FOLDER"], '{csvfilename}'.format(csvfilename = editedfilename))))
                            zipObj2.write(logsavepath, basename(logsavepath))
                            # zipObj2.write(os.path.join(app.config["UPLOAD_FOLDER"], filename), basename(os.path.join(app.config["UPLOAD_FOLDER"], filename)))
                        print('1013 - done zip')
                        storedzipfile = '{zipfilename}.zip'.format(zipfilename = urlfilename)
                        
                        if option == '1':
                            resp = make_response(send_file(os.path.join(app.config["UPLOAD_FOLDER"], '{zipfilename}.zip'.format(zipfilename = urlfilename))))
                            resp.headers["Content-Disposition"] = "attachment; filename={zipfilename}.zip".format(zipfilename = urlfilename)
                            resp.headers["Content-Type"] = "application/zip"
                            return resp
                        elif option == '2':
                            return render_template("page.html",
                                                # filehexprint = '::::::::: '.join(stringtry),
                                                auth_info=auth_info,
                                                path_prefix=path_prefix,
                                                submitbuttondisplay = 'hide',
                                                submitbuttonpressed = '',
                                                csvdownload = '',
                                                datacsvcsv=csv_reader,
                                                # d1=d1,
                                                # file=storedzipfile,
                                                # message = 'Success, download updated csv file and log file here',
                                                # message_file= "Uploaded file: {}".format(front.filename),
                                                # message_place= "Please find the updated file in C:/Downloads after downloading by clicking on the below buttons" 
                                                # message_place= "Opening the log file in excel will display ???, please set the csv to utf-8-BOM in notepad++ to see Chinese characters in excel"
                                                )
                        elif option == '3':
                            return render_template("page.html",
                                                auth_info=auth_info,
                                                path_prefix=path_prefix,
                                                submitbuttondisplay = 'hide',
                                                submitbuttonpressed = '',
                                                csvdownload = '',
                                                datacsvcsv=log_reader)
            except Exception as e:
                print(e)
                print('1004')
                return render_template('page.html',
                                submitbuttondisplay = 'show',
                                submitbuttonpressed = '',
                                datacsvcsv = '',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                message_failed = 'Unexpected Error. Please double check uploaded file.'
                                )
        else:
            print('1004')
            return render_template('page.html',
                                submitbuttondisplay = 'show',
                                submitbuttonpressed = '',
                                datacsvcsv = '',
                                auth_info=auth_info,
                                path_prefix=path_prefix,
                                csvdownload = "",
                                message_failed = 'Please upload a csv file')


# @app.route('/<hex>/<file>')
# def zip_download(hex, file):
#     # return send_from_directory(app.config["UPLOAD_FOLDER"], file, as_attachment=True)
#     resp = make_response(send_file(os.path.join(app.config["UPLOAD_FOLDER"], '{zipfilename}'.format(zipfilename = file))))
#     resp.headers["Content-Disposition"] = "attachment; filename={zipfilename}".format(zipfilename = file)
#     resp.headers["Content-Type"] = "application/zip"
    # return resp  #Return zip file to user

# @app.route('/result/downloadcsv', methods=['GET', 'POST'])
# def downloadcsv():
#     if request.method == 'GET':
#         resp = make_response(send_file(os.path.join(app.config["UPLOAD_FOLDER"], '{csvfilename}'.format(csvfilename = front.editedfilename))))
#         resp.headers["Content-Disposition"] = "attachment; filename={csvfilename}".format(csvfilename = front.editedfilename)
#         resp.headers["Content-Type"] = "text/csv"
#         return resp

# @app.route('/result/downloadlog', methods=['GET', 'POST'])
# def downloadlog():
#     if request.method == 'GET':
#         resp = make_response(send_file(front.logsavepath))
#         resp.headers["Content-Disposition"] = "attachment; filename={logfilename}".format(logfilename = front.logfilename)
#         resp.headers["Content-Type"] = "text/csv"
#         return resp


if __name__ == '__main__':
    app.run(debug=True)
