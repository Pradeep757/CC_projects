#Use of alpine 3.7
FROM alpine:3.7

#Installing packages
RUN apk add --no-cache python3 && \
    python3 -m ensurepip && \
    pip3 install flask && \
    pip3 install flask-cors && \
    pip3 install requests

#working directory is /app
WORKDIR /app

#Copying pwd contents into the container at /app
COPY . /app

EXPOSE 80

ENV TEAM_ID CC_254_264_267_268

#Run users.py when container launches
CMD ["python3", "acts.py"]
