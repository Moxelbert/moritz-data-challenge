# Use the slim version of the node 14 image as our base
FROM node:14-slim

# Create a directory for our application in the container 
WORKDIR /usr/src/app

# Copy package.json and package-lock.json first to leverage Docker cache
COPY package*.json ./

# Install only production dependencies
RUN npm install --only=production

# Copy the rest of the application files
COPY . .

# Build the React app
RUN npm run build

# Install 'serve', a static file serving package globally in the container
RUN npm install -g serve

# Cloud Run expects the application to listen on port 8080
ENV PORT 8080

# Expose the port for Cloud Run
EXPOSE 8080

# Serve the 'build' directory using 'serve'
CMD ["serve", "-s", "-l", "8080", "build"]
