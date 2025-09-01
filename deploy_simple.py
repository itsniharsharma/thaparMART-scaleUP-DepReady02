#!/usr/bin/env python3
"""
Simple Docker Deployment - No Complex Build Process
Uses basic Docker setup without fancy multi-stage builds
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def create_simple_frontend_dockerfile():
    print("📝 Creating simple frontend Dockerfile...")
    
    dockerfile_content = """# Simple Node.js setup
FROM node:18-alpine

WORKDIR /app

# Copy package.json only
COPY package.json ./

# Install dependencies with retries
RUN npm install --legacy-peer-deps --no-package-lock

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Serve using simple http server
RUN npm install -g serve

EXPOSE 3000

CMD ["serve", "-s", "build", "-l", "3000"]
"""
    
    with open("frontend/Dockerfile", "w") as f:
        f.write(dockerfile_content)
    print("✅ Created simple Dockerfile")

def create_simple_docker_compose():
    print("📝 Creating simple docker-compose...")
    
    compose_content = """version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:latest
    container_name: thapar-mongodb-simple
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: thaparmart2024
      MONGO_INITDB_DATABASE: thaparMARTN
    volumes:
      - mongodb_data_simple:/data/db

  # FastAPI Backend
  backend:
    build: ./backend
    container_name: thapar-backend-simple
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:thaparmart2024@mongodb:27017/thaparMARTN?authSource=admin
      - DB_NAME=thaparMARTN
      - CORS_ORIGINS=http://localhost:3000,http://localhost:80
      - AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
      - AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY
      - AWS_REGION=ap-south-1
      - S3_BUCKET_NAME=thaparmart-local
      - RAZORPAY_KEY_ID=rzp_test_RC0rOzm4xN5Drr
      - RAZORPAY_KEY_SECRET=2wfEhHUe4ZYuPsx7RgaWvGXi
    depends_on:
      - mongodb

  # React Frontend (Simple)
  frontend:
    build: ./frontend
    container_name: thapar-frontend-simple
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend

volumes:
  mongodb_data_simple:
"""
    
    with open("docker-compose-simple.yml", "w") as f:
        f.write(compose_content)
    print("✅ Created simple docker-compose")

def deploy_simple():
    print("=" * 60)
    print("🚀 THAPAR MARKETPLACE - SIMPLE DEPLOYMENT")
    print("=" * 60)
    
    try:
        # Create simple configurations
        create_simple_frontend_dockerfile()
        create_simple_docker_compose()
        
        # Stop any existing containers
        print("\n🛑 Stopping existing containers...")
        subprocess.run(['docker-compose', '-f', 'docker-compose-simple.yml', 'down'], check=False)
        
        # Build and start
        print("\n🔨 Building and starting services (simple mode)...")
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose-simple.yml', 
            'up', '--build', '-d'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Services started successfully!")
            
            # Wait for services
            print("\n⏳ Waiting for services to be ready...")
            time.sleep(15)
            
            print("\n🌐 Your Thapar Marketplace is running!")
            print("=" * 50)
            print("📱 Frontend:      http://localhost:3000")
            print("🔧 Backend API:   http://localhost:8001")
            print("🗄️  Database:     localhost:27017")
            print("=" * 50)
            
            print("\n📋 Commands:")
            print("   View logs:     docker-compose -f docker-compose-simple.yml logs -f")
            print("   Stop services: docker-compose -f docker-compose-simple.yml down")
            
        else:
            print("❌ Failed to start services:")
            print(result.stderr)
            print("\n🆘 Try these fixes:")
            print("1. Restart Docker Desktop")  
            print("2. Run: docker system prune -a")
            print("3. Check Docker has 4GB+ memory allocated")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    deploy_simple()