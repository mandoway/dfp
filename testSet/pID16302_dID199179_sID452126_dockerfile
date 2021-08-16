FROM ubuntu

RUN mkdir /src
WORKDIR /src

# For this: npm install sharp randomstring --save (installing via package.json)
RUN apt-get update
RUN apt-get install curl -y 
RUN apt-get install pkg-config -y
RUN curl -s https://raw.githubusercontent.com/lovell/sharp/master/preinstall.sh | sudo bash -


RUN curl -sL https://deb.nodesource.com/setup_5.x | sudo -E bash -
RUN apt-get install -y nodejs build-essential


# prepare build
ADD package.json package.json
RUN npm install
RUN rm package.json

RUN npm install rimraf -g 
RUN npm install webpack -g 




# connect resources
ADD . ./

# RUN npm start

# RUN mkdir /var/glossary
RUN mkdir -p /var/glossary/uploads
VOLUME "/var/glossary/uploads"

# share port
EXPOSE 3000

# RUN rimraf dist && NODE_ENV=production webpack --config ./webpack.production.config.js --progress --profile --colors
# run app
CMD ["npm", "start"]
