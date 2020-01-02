from flask import Flask, render_template,request,abort,jsonify,Response,make_response
from flask_cors import CORS
import json
import csv
import sys
import base64


app = Flask(__name__)
CORS(app)
 
csv.field_size_limit(sys.maxsize)


def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/users',methods=['GET','POST'])
def add_user():
	if request.method == 'POST':
		if request.headers['Content-Type'] == 'application/x-www-form-urlencoded':
			data = request.form
			row = [data["username"],data["password"]]
			if is_sha1(data["password"])==False:
				return Response(status=400,mimetype='application/json')
			with open('users.csv', 'a') as csvFile:
				writer = csv.writer(csvFile)
				writer.writerow(row)
			return Response(status=201,mimetype='application/json')

		elif request.headers['Content-Type'] == 'application/json':
			try:
				#print("in")
				data = request.json
				row = [data["username"],data["password"]]
				if is_sha1(data["password"])==False:
					print("false")
					return Response(status=400,mimetype='application/json')
				with open('users.csv', 'r+') as csvFile:
					reader = csv.reader(csvFile)
					for line in reader:
						if line[0]==row[0]:
							return Response(status=400,mimetype='application/json')
					writer = csv.writer(csvFile)
					writer.writerow(row)
				return Response(status=201,mimetype='application/json')
			except Exception as e:
				print(e)
				return Response(status=400,mimetype='application/json')
		#return jsonify(request.form)
		#return jsonify(request.form)
	elif request.method == 'GET':
		try:
			line = []
			with open("users.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for i in reader:
					line.append(i[0])

			if len(line)==0:
				return Response(status=204,mimetype='application/json')
			#print(line)
			#line = jsonify(line)

			response = make_response(json.dumps(line),200)
			response.headers['content-type'] = 'application/json'
			return response;
		except FileNotFoundError:
			return Response(status=204,mimetype='application/json')


@app.route('/api/v1/users/<username>',methods=['DELETE'])
def rem_user(username):
	try:
		lines = []
		flag=0
		with open("users.csv","r") as csvFile:
			reader = csv.reader(csvFile)
			for line in reader:
				if line[0]!=username:
					lines.append(line)
				elif line[0]==username:
					flag=1
		with open("users.csv","w") as csvFile:
			writer = csv.writer(csvFile)
			for l in lines:
				writer.writerow(l)
		if flag==0:
			return Response(status=400,mimetype='application/json')
		else:
			response = make_response(jsonify({}),200)
			response.headers['content-type'] = 'application/json'
			return response
	except FileNotFoundError:
		return Response(status=400,mimetype='application/json')	


if __name__ == '__main__':
	app.run(host='0.0.0.0',port=80)