FROM node:14-slim
WORKDIR /usr/src/app
COPY package*.json ./
RUN npm install --only=production
COPY . .
RUN npm run build
RUN npm install -g serve
ENV PORT 8080
EXPOSE 8080
CMD ["serve", "-s", "-l", "8080", "build"]