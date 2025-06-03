FROM node:lts-alpine

WORKDIR /app

COPY . .
RUN npm install

ENTRYPOINT [ "node", "index.js" ]
