"""
This version is optimized for operation with the Apache WSGI module. You need to rewrite it to work on a local instance of flask.
Some info such as paths have been changed for security reasons.


MIT License

Copyright (c) 2017 Kevin Christen (Purpl3.net)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


"""
import os
import ssl
import uuid
import threading
import time
# We'll render HTML templates and access data sent by POST
# using the request object from flask. Redirect and url_for
# will be used to redirect the user once the upload is done
# and send_from_directory will help us to send/show on the
# browser the file that the user just uploaded
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import bitarray


# Initialize the Flask application
app = Flask(__name__)

# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = '/uploads/'
# These are the extension that we are accepting to be uploaded
app.config['ALLOWED_EXTENSIONS'] = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'inv', 'mp3', 'doc', 'docx', 'ppt', 'pptx', 'tar', 'gz', '7z', 'zip', 'rar', 'rtf', 'tgz', 'xml', 'json', 'xls', 'xlsx', 'msg'])
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024

# For a given file, return whether it's an allowed type or not
def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
	return render_template('index.html')

def readinchunks(inputfile, chunk=1024*1024):
	while True:	
		data = inputfile.read(chunk)
		if not data:
			break
		yield data

def removeFile(filename):
	time.sleep(600)
	os.remove(filename)	

def inverter(inputpath,outputpath):
	#open file
	bytefile = open(inputpath, "rb")
	#open outputpath and immediately close it and open it back up as 'ab'(append binary)
	outputfile = open(outputpath, "wb")
	outputfile.close()
	outputfile = open(outputpath, "ab")
	#loop that goes through each chunk, inverts the bits and appends it to the output file.
	for piece in readinchunks(bytefile):
		#bitarray is convenient since it can easily convert files to bitarrays. 'a' is a bitarray
		a = bitarray.bitarray()
		#gets bytes from chunk 
		a.frombytes(piece)
		#converts all bits of chunk to array ex: [True, False, False, True , etc.] and save it as BitsToList
		BitsToList = a.tolist()
		#inverts True to False and False to True
		inversion = [not x for x in BitsToList]
		#creates a new bitarray from the altered Array 'inversion'
		backToBits = bitarray.bitarray(inversion)
		#writes the changes to the output file
		backToBits.tofile(outputfile)
		#sets a to an empty bitarray and inversion to None to prevent memory leak.
		a = bitarray.bitarray()
		inversion = None
	#closes the file and finishes the process
	outputfile.close()

# Route that will process the file upload
@app.route('/upload', methods=['POST'])
def upload():
    	# Get the name of the uploaded file
	file = request.files['file']
    	# Check if the file is one of the allowed types/extensions
	if file and allowed_file(file.filename):
        	# Make the filename safe, remove unsupported chars
		filename = secure_filename(file.filename)
        	# Move the file form the temporal folder to
        	# the upload folder we setup
		file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
		#invert file
		#generate random name
		rndname = str(uuid.uuid4())
		inverter("/uploads/"+filename, "/uploads/"+rndname+".inv")
		#start thread to remove inversion after a certain time
		removeThread = threading.Thread(target=removeFile , args=["/uploads/"+rndname+".inv"])
		removeThread.start()
		#remove original upload after inversion
		os.remove("/uploads/"+filename)
        	# Redirect the user to the uploaded_file route, which
        	# will basicaly show on the browser the uploaded file
		return redirect(url_for('uploaded_file',filename=rndname+".inv"))

# This route is expecting a parameter containing the name
# of a file. Then it will locate that file on the upload
# directory and show it on the browser, so if the user uploads
# an image, that image is going to be show after the upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
	return send_from_directory(app.config['UPLOAD_FOLDER'],filename)

if __name__ == '__main__':
	app.run()

