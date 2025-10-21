# Use Node 18 LTS as base image
FROM node:18

# Install ping and netcat tools
RUN apt-get update && apt-get install -y iputils-ping netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy package files first for caching
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy application source code
COPY . .

# Expose your service port
EXPOSE 3001

# Start the application
CMD ["node", "server.js"]
