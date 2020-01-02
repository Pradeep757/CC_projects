from flask import Flask, render_template,request,abort,jsonify,Response,make_response
import requests
import json
from flask_cors import CORS
import threading
import time
import subprocess

app = Flask(__name__)
CORS(app)

containers = [8000]

ip_addr = 'localhost'
port_no = 8000
count = 0

def monitor():
	global count,containers
	while True:
		if count > 0:
			print("timer started")
			time.sleep(120)
			for i in range(1,11):
				if count < 20*i and count>=20*(i-1):
					if i==len(containers):
						break
					elif i<len(containers):
						k = len(containers)
						for j in range(k,i,-1):
							cmd = 'sudo docker container stop acts'+str(j)
							subprocess.call(cmd.split())
							cmd = 'sudo docker container rm acts'+str(j)
							subprocess.call(cmd.split())
							del containers[j-1]
					elif i>len(containers):
						k = len(containers)
						for j in range(k,i):
							cmd = 'sudo docker run -d -p 800'+str(k)+':80 --name=acts'+str(k+1)+' --mount source=data1,destination=/app acts' 
							subprocess.call(cmd.split())
							containers.append(containers[k-1]+1)
			count = 1


def fault_tolerance():
	global containers
	while True:
		time.sleep(1)
		 for i in containers:
                        try:
                                r = requests.get('http://localhost:'+str(i)+'/api/v1/_health')
                                if r.status_code == 500:
                                        print("restarting container at port"+str(i))
                                        cm = 'sudo docker container stop acts'+str((i%10 )+ 1)
                                        subprocess.call(cm.split())
                                        cm = 'sudo docker container rm acts'+str((i%10 )+ 1)
                                        subprocess.call(cm.split())
                                        cm = 'sudo docker run -d -p '+str(i)+':80 --name=acts'+str((i%10 )+ 1)+' --mount source=data1,destination=/app acts'
                                        subprocess.call(cm.split())
                        except:
                                pass

		



@app.route('/api/v1/categories',methods=['GET','POST'])
def forword_cat():
	global count,port_no,containers
	port_no = containers[count%len(containers)]
	count = count +1
	if request.method == 'GET':
		#print(request.host_url)
		resp = requests.get('http://'+ip_addr+':'+str(port_no)+'/api/v1/categories')
		response = Response(resp.content, resp.status_code)
		return response
	elif request.method == 'POST':
		#print(request.json,type(request.json))
		#print(json.dumps(request.json))
		head={key: value for (key, value) in request.headers if key != 'Host'}
		head['Content-Type'] = 'application/json'
		resp = requests.post('http://'+ip_addr+':'+str(port_no)+'/api/v1/categories',data=json.dumps(request.json),headers=head)
		response = Response(resp.content, resp.status_code)
		return response


"""resp = requests.request(
        method=request.method,
        url=request.url.replace(request.host_url, 'new-domain.com'),
        headers={key: value for (key, value) in request.headers if key != 'Host'},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False)"""

@app.route('/api/v1/categories/<categoryName>',methods=['DELETE'])
def forword_catdel(categoryName):
	global count,port_no,containers
	port_no = containers[count%len(containers)]
	count = count +1
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
			method=request.method,\
			url = request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
			headers = head)
	response = Response(resp.content,resp.status_code)
	return response

@app.route('/api/v1/acts',methods=['POST'])
@app.route('/api/v1/acts/upvote',methods=['POST'])
def forword_acts():
	global count,port_no,containers
	port_no = containers[count%len(containers)]
	count = count +1
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		data=json.dumps(request.json),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response

@app.route('/api/v1/categories/<categoryName>/acts/size',methods=['GET'])
@app.route('/api/v1/categories/<categoryName>/acts',methods=['GET'])
def forword_acts_size(categoryName):
	global count,port_no,containers
	port_no = containers[count%len(containers)]
	count = count +1
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response

'''@app.route('/api/v1/categories/<categoryName>/acts',methods=['GET'])
def forword_acts_in_cat(categoryName):
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response
	
@app.route('/api/v1/acts/upvote',methods=['POST'])
def forword_upvote():
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		data=json.dumps(request.json),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response'''

@app.route('/api/v1/acts/<int:actId>',methods=['DELETE'])
def forword_remove_act(actId):
	global count,port_no,containers
	port_no = containers[count%len(containers)]
	count = count +1
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response


@app.route('/api/v1/_health',methods=['GET'])
def forword_health():
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response

@app.route('/api/v1/_crash',methods=['POST'])
def forword_crash():
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	head['Content-Type'] = 'application/json'
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		data=json.dumps(request.json),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response
'''
@app.route('/api/v1/_count',methods=['GET','DELETE'])
def forword_count():
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response

@app.route('/api/v1/acts/count',methods=['GET'])
def forword_acts_count():
	head = {key: value for (key, value) in request.headers if key != 'Host'}
	resp = requests.request(\
		method=request.method,\
		url=request.url.replace(request.host_url, 'http://'+ip_addr+':'+str(port_no)+'/'),\
		headers=head)
	response = Response(resp.content,resp.status_code)
	return response'''





if __name__ == '__main__':
	monitoring_thread = threading.Thread(target = monitor)
	monitoring_thread.start()
	fault_tolerance= threading.Thread(target = fault_tolerance)
	fault_tolerance.start()
	app.run(debug=False,host='0.0.0.0',port=5000)