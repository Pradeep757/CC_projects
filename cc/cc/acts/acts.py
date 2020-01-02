from flask import Flask, render_template,request,abort,jsonify,Response,make_response
from flask_cors import CORS
import json
import csv
import sys
import base64
import requests


app = Flask(__name__)
CORS(app)   
 
csv.field_size_limit(sys.maxsize)

count_requests = 0
crash = 0

def isBase64(sb):
        try:
                if type(sb) == str:
                        # If there's any unicode here, an exception will be thrown and the function will return false
                        sb_bytes = bytes(sb, 'ascii')
                elif type(sb) == bytes:
                        sb_bytes = sb
                else:
                        raise ValueError("Argument must be string or bytes")
                return base64.b64encode(base64.b64decode(sb_bytes)) == sb_bytes
        except Exception:
                return False

def check_timestamp(time):
	try:
		#print('debug',time)
		t = time.strip().split(":")
		date = t[0].split("-")
		tm = t[1].split("-")
		flag = 0
		#print("debug")
		#print(date[0],len(date[0]),date[1],len(date[1]),date[2],len(date[2]),tm[0],len(tm[0]),tm[1],len(tm[1]),tm[2],len(tm[2]))
		if len(date[0])!=2 or int(date[0])>31 or int(date[0])<0:
			print("1")
			return False
		if len(date[1])!=2 or int(date[1])>12 or int(date[1])<0:
			return False
		if len(date[2])!=4:
			return False
		if len(tm[0])!=2 or int(tm[0])>60 or int(tm[0])<0:
			return False
		if len(tm[1])!=2 or int(tm[1])>60 or int(tm[1])<0:
			return False
		if len(tm[2])!=2 or int(tm[2])>24 or int(tm[2])<0:
			return False
		return True
	except Exception as e:
		#print(e)
		return False

def isCategoryExist(categoryName):
	with open("categories.csv","r") as csvFile:
		reader = csv.reader(csvFile)
		for line in reader:
			if line[0]==categoryName:
				return True
	return False


def actsInCategory(categoryName):
	count=0
	with open("acts.csv","r") as csvFile:
		reader = csv.reader(csvFile)
		for line in reader:
			if line[4]==categoryName:
				count+=1
	return count

def date_time(time):
	try:
		t = time.strip().split(":")
		date = t[0].split("-")
		tm = t[1].split("-")
		string = date[2]+'-'+date[1]+'-'+date[0]+ ' '+tm[2]+':'+tm[1]+':'+tm[0]
		return string
	except:
		return False

def is_sha1(maybe_sha):
    if len(maybe_sha) != 40:
        return False
    try:
        sha_int = int(maybe_sha, 16)
    except ValueError:
        return False
    return True

@app.route('/api/v1/categories',methods=['GET','POST'])
def list_categories():
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	if request.method == 'GET':
		try:
			dic = {}
			with open("categories.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					try:
						dic[line[0]]=0
					except IndexError:
						return Response(status=204,mimetype='application/json')
			with open("acts.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					try:
						dic[line[4]]=int(dic[line[4]])+1
					except KeyError:
						continue
			if len(dic)==0:
				return Response(status=204,mimetype='application/json')
			dic = jsonify(dic)

			response = make_response(dic,200)
			response.headers['content-type'] = 'application/json'
			return response;
		except FileNotFoundError:
			return Response(status=204,mimetype='application/json')
	elif request.method == 'POST':
		try:
			response = make_response(jsonify({}),201)
			response.headers['content-type'] = 'application/json'
			data = request.json
			if len(data)!=1:
				return Response(status=400,mimetype='application/json')
			category = data[0]
			l = [category,0]
			with open("categories.csv","r+") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					if line[0]==category:
						return Response(status=400,mimetype='application/json')
				writer = csv.writer(csvFile)
				writer.writerow(l)
			return response
		except:
			return Response(status=400,mimetype='application/json')

@app.route('/api/v1/categories/<categoryName>',methods=['DELETE'])
def rem_category(categoryName):
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	try:
		lines = []
		flag=0
		with open("categories.csv","r") as csvFile:
			reader = csv.reader(csvFile)
			for line in reader:
				if line[0]!=categoryName:
					lines.append(line)
				elif line[0]==categoryName:
					flag=1
		with open("categories.csv","w") as csvFile:
			writer = csv.writer(csvFile)
			for l in lines:
				writer.writerow(l)
		if flag==0:
			return Response(status=400,mimetype='application/json')
		else:
			response = make_response(jsonify({}),200)
			response.headers['content-type'] = 'application/json'
			return response
	except:
		return Response(status=400,mimetype='application/json')


@app.route('/api/v1/acts',methods=['POST'])
def upload_act():
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	data = request.json
	#print(data)
	try:
		if len(data)!=6:
			return Response(status=400,mimetype='application/json')
		try:
			flag=0
			actId = data["actId"]
			username = data["username"]
			timestamp = data["timestamp"]
			caption = data["caption"]
			categoryName = data["categoryName"]
			imgB64 = data["imgB64"]
			'''with open("users.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					if line[0]==username:
						flag=1'''
			#print('username')
			headers = {'Origin': 'ec2-54-87-248-40.compute-1.amazonaws.com'}
			uri = 'http://3.210.49.79:80/api/v1/users'
			r = requests.get(url=uri,headers=headers)
			#print(r)
			data = r.json()
			#print(data)
			for i in data:
				if i==username:
					flag=1
			if flag==0:
				return Response(status=400,mimetype='application/json')
			#print("user validated")

			flag=0
			with open("categories.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					if line[0]==categoryName:
						flag=1
			if flag==0:
				return Response(status=400,mimetype='application/json')
			#print("category validated")
			if isBase64(imgB64)!=True:
				return Response(status=400,mimetype='application/json')
			#print("Base64")
			if check_timestamp(timestamp)!=True:
				return Response(status=400,mimetype='application/json')
			#print("timestamp")
			with open("acts.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					if int(line[0])==int(actId):
						#print("same act id")
						return Response(status=400,mimetype='application/json')
			#print("actid")
			row = [actId,username,timestamp,caption,categoryName,imgB64,0]
			with open("acts.csv","a") as csvFile:
				writer = csv.writer(csvFile)
				writer.writerow(row)
			response = make_response(jsonify({}),201)
			response.headers['content-type'] = 'application/json'
			return response

		except Exception as e:
			print(e)
			return Response(status=400,mimetype='application/json')
	except TypeError:
			return Response(status=400,mimetype='application/json')



@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
def actsincategory(categoryName):
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	if isCategoryExist(categoryName)!=True:
		return Response(status=400,mimetype='application/json')
	arr = []
	arr.append(actsInCategory(categoryName))
	return Response(json.dumps(arr),200,mimetype='application/json')

'''@app.route('/api/v1/categories/<categoryName>/acts?start=<int:startRange>&end=<int:endRange>',methods=['GET'])
def list_acts_inRange(categoryName,startRange,endRange):
	try:
		if isCategoryExist(categoryName)!=True:
			return Response(status=204,mimetype='application/json')
		if startRange<1 or endRange>actsInCategory(categoryName):
			return Response(status=400,mimetype='application/json')
		if endRange-startRange+1 >100:
			return Response(status=413,mimetype='application/json')
		arr = []
		with open("acts.csv","r") as csvFile:
			reader = csv.reader(csvFile)
			for line in reader:
				data = dict()
				if line[4]==categoryName:
					#data["actId"] = line[0]
					#data["username"] = line[1]
					data["timestamp"] = line[2]
					#data["caption"] = line[3]
					#data["upvotes"] = line[6]
					#data["imgB64"] = line[5]
					arr.append(data)
		if len(arr)==0:
			return Response(status=204,mimetype='application/json')
		sorted_arr = sorted(arr,key = lambda val:date_time(val["timestamp"]),reverse=True)
		sorted_arr = sorted_arr[startRange:endRange+1]
		response = make_response(json.dumps(sorted_arr),200)
		response.headers['content-type'] = 'application/json'
		return response

	except:
		return Response(status=400,mimetype='application/json')'''


@app.route('/api/v1/categories/<categoryName>/acts',methods=['GET'])
def list_acts(categoryName):
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	if len(request.args)==0:
		print(len(request.args),request.args)
		try:
			if isCategoryExist(categoryName)!=True:
				return Response(status=204,mimetype='application/json')
			#print("category validate")
			if actsInCategory(categoryName)>100:
				return Response(status=413,mimetype='application/json')
			#print("acts validated")
			arr = []
			with open("acts.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					data = dict()
					if line[4]==categoryName:
						data["actId"] = int(line[0])
						data["username"] = line[1]
						data["timestamp"] = line[2]
						data["caption"] = line[3]
						data["upvotes"] = int(line[6])
						data["imgB64"] = line[5]
						arr.append(data)
			#print("debug")
			#print(len(arr))
			if len(arr)==0:
				return Response(status=204,mimetype='application/json')
			arr = sorted(arr,key = lambda val:date_time(val["timestamp"]),reverse=True)
			response = make_response(json.dumps(arr),200)
			response.headers['content-type'] = 'application/json'
			return response
		except Exception as e:
			#print(e)
			return Response(status=204,mimetype='application/json')
	else:
		try:
			startRange = int(request.args.get('start'))
			endRange = int(request.args.get('end'))
			if isCategoryExist(categoryName)!=True:
				return Response(status=204,mimetype='application/json')
			if startRange<1 or endRange>actsInCategory(categoryName):
				return Response(status=400,mimetype='application/json')
			if endRange-startRange+1 >100:
				return Response(status=413,mimetype='application/json')
			#print("DEBUG")
			arr = []
			with open("acts.csv","r") as csvFile:
				reader = csv.reader(csvFile)
				for line in reader:
					data = dict()
					if line[4]==categoryName:
						data["actId"] = int(line[0])
						data["username"] = line[1]
						data["timestamp"] = line[2]
						data["caption"] = line[3]
						data["upvotes"] = int(line[6])
						data["imgB64"] = line[5]
						arr.append(data)
			if len(arr)==0:
				return Response(status=204,mimetype='application/json')
			sorted_arr = sorted(arr,key = lambda val:date_time(val["timestamp"]),reverse=True)
			sorted_arr = sorted_arr[startRange-1:endRange]
			response = make_response(json.dumps(sorted_arr),200)
			response.headers['content-type'] = 'application/json'
			return response

		except Exception as e:
			print(e)
			return Response(status=400,mimetype='application/json')

				


@app.route('/api/v1/acts/upvote',methods=['POST'])
def upvoteAct():
	global count_requests,crash
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1

	try:
		response = make_response(jsonify({}),200)
		response.headers['content-type'] = 'application/json'
		data = request.json
		#print(data)
		actId = data[0]
		#print(actId)
		lines = []
		flag=0
		if len(data)!=1:
			return Response(status=400,mimetype='application/json')
		with open("acts.csv","r+") as csvFile:
			reader = csv.reader(csvFile)
			for line in reader:
				if int(line[0])==int(actId):
					#print("in")
					line[6] = int(line[6])+1
					lines.append(line)
					flag=1
				else:
					lines.append(line)
		if flag==0:
			print("flag")
			return Response(status=400,mimetype='application/json')
		with open("acts.csv","w") as csvFile:
			writer = csv.writer(csvFile)
			for i in lines:
				writer.writerow(i)
		return response
	except Exception as e:
		#print(e)
		return Response(status=400,mimetype='application/json')

	

@app.route('/api/v1/acts/<int:actId>',methods=['DELETE'])
def removeAct(actId):
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	try:
		lines=[]
		flag=0
		with open('acts.csv',"r") as csvFile:
			reader = csv.reader(csvFile)
			for line in reader:
				if int(line[0])==actId:
					flag=1
				else:
					lines.append(line)
		if flag==0:
			return Response(status=400,mimetype='application/json')
		with open('acts.csv',"w") as csvFile:
			writer = csv.writer(csvFile)
			for i in lines:
				writer.writerow(i)
		response = make_response(jsonify({}),200)
		response.headers['content-type'] = 'application/json'
		return response
	except Exception as e:
		print(e)
		return Response(status=400,mimetype='application/json')	


@app.route('/api/v1/_count',methods=['GET','DELETE'])
def counts():
	global count_requests,crash
	if crash!=0:
		return Response(status=500)
	if request.method == 'GET':
		response = make_response(json.dumps([count_requests]),200)
		response.headers['content-type'] = 'application/json'
		return response
	elif request.method == 'DELETE':
		count_requests=0
		return Response(status=200,mimetype='application/json')	

@app.route('/api/v1/acts/count',methods=['GET'])
def acts_count():
	global count_requests,crash
	
	if crash!=0:
		return Response(status=500)
	count_requests = count_requests+1
	c=0
	with open('acts.csv',"r") as csvFile:
		reader = csv.reader(csvFile)
		for line in reader:
			c = c+1
	response = make_response(json.dumps([c]),200)
	response.headers['content-type'] = 'application/json'
	return response

@app.route('/api/v1/_health',methods=['GET'])
def health():
	global crash
	if crash!=0:
		return Response(status=500)
	return Response(status=200)

@app.route('/api/v1/_crash',methods=['POST'])
def crash_server():
	global crash
	if crash!=0:
		return Response(status=500)
	crash=1
	return Response(status=200)



if __name__ == '__main__':
	app.run(debug=False,host='0.0.0.0',port=80)
