from flask import Flask, request,url_for
from flask_uploads import UploadSet, IMAGES
from flask_restful import Api, Resource, reqparse
from werkzeug.utils import secure_filename
from AutoGenerate import AutoGenerate
from flask_cors import CORS
from time import strftime

'''Illustration about this api

1. For first time upload:

POST request with api Key
{ photo: Multipart data,
width: int,
height: int,
widthheightratio: float,
colortype: "BW" , "BWG" or "MULTI",
colorchoice:{#001000,#902001,#299003,(...)}
}

Response is 
{ photo: as Multipart data .bmp file,
id: string,
message: String 
}

2. For second time upload:

PATCH request with api Key
{ id: string(the id of photo you want to modify),
width: int,
height: int,
widthheightratio: float,
colortype: "BW" , "BWG" or "MULTI",
colorchoice:{#001000,#902001,#299003,(...)}
}

Response is 
{ photo: as Multipart data .bmp file,
id: string (the id of photo you want to modified),
message: String 
}




'''


app = Flask(__name__)
CORS(app)
api = Api(app)

photos = UploadSet('photos', IMAGES)


def modify_recieved_post(self):

    if 'photo' not in request.files:
        response = {"success": False, 'message': 'No file part'}
        return response, 500

    if request.method == 'POST' and 'photo' in request.files:
        thisfile = request.files['photo']
        thisfile.filename = thisfile.filename.lower()
        try:
            filename = photos.save(
                thisfile, name=secure_filename(thisfile.filename))
        except:
            response = {"success": False, 'message': 'Upload Not Allowed'}
            print('Upload Not Allowed')
            return response, 500

        parser = reqparse.RequestParser()
        parser.add_argument("width")
        parser.add_argument("height")
        parser.add_argument("widthheightratio")
        args = parser.parse_args()
        newname = str(hash(filename))+'.bmp'
        (flag, width, height, widthratio) = AutoGenerate(inputpath=app.config['UPLOADED_PHOTOS_DEST']+'/'+filename,
        outputpath=app.config['CHANGED_PHOTOS_DEST']+'/'+newname,
        widthheightratio=float(args['widthheightratio']),
        outputpixelWidth=int(args['width']),
        outputpixelHeight=int(args['height']))

        # def AutoGenerate(inputpath ='static/img/importfile.jpg',outputname = 'static/trans/outputfile.bmp',threshhold = 0,brightness=0,contrast = 0,widthheightratio = 1.307,outputpixelWidth=133,outputpixelHeight=114 ):
        response = {
            "success": True,
            'id': filename,
            'url': url_for('transformed_file', filename=newname),
            "width": width,
            "height": height,
            "widthratio": widthratio,
            "newid": newname
        }
        return response, 201
    response = {"success": False, 'message': 'Not correct file type'}
    return response, 500

class Upload(Resource):
    def post(self):
        return modify_recieved_post(self)

api.add_resource(Upload, "/")

def modify_photo_patch(self, id):
    parser = reqparse.RequestParser()
    parser.add_argument("contrast")
    parser.add_argument("brightness")
    parser.add_argument("threshold")
    parser.add_argument("width")
    parser.add_argument("height")
    parser.add_argument("widthheightratio")
    args = parser.parse_args()
    newId = strftime("%a%d%b%Y%H%M%S")+str(hash(id))+'.bmp'
    (flag, width, height, widthratio) = AutoGenerate(inputpath=app.config['UPLOADED_PHOTOS_DEST']+'/'+id,
                                                        outputpath=app.config['CHANGED_PHOTOS_DEST']+'/'+newId,
                                                        threshhold=int(float(args['threshold'])),
                                                        brightness=int(float(args['brightness'])),
                                                        contrast=int(float(args['contrast'])),
                                                        widthheightratio=float(args['widthheightratio']),
                                                        outputpixelWidth=int(args['width']),
                                                        outputpixelHeight=int(args['height']))

    if flag:
        response = {
                "id": id,
                "success": True,
                "url": url_for('transformed_file', filename=newId),
                'newid': newId
            }
            # response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            # response.cache_control.no_cache = True
        return response, 200
    else:
        response = {
                "id": id,
                "success": False
            }
        return response, 500

class ShowResult(Resource):
    def patch(self, id):
        return modify_photo_patch(self, id)


api.add_resource(ShowResult, "/<string:id>")
if __name__ == '__main__':
    app.run()
