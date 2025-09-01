#!/usr/bin/env python3
"""
Thapar Marketplace - Local Deployment Script
Run with: python deploy_local.py
"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path

class LocalDeployment:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.compose_file = self.project_root / "docker-compose.yml"
        
    def print_banner(self):
        print("=" * 60)
        print("🚀 THAPAR MARKETPLACE - LOCAL DEPLOYMENT")
        print("=" * 60)
        
    def check_prerequisites(self):
        print("\n🔍 Checking prerequisites...")
        
        # Check if Docker is installed
        try:
            result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker found: {result.stdout.strip()}")
            else:
                raise Exception("Docker not found")
        except Exception:
            print("❌ Docker is not installed or not running!")
            print("\n📥 Install Docker:")
            print("   Windows/Mac: Download Docker Desktop from https://docker.com")
            print("   Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh")
            sys.exit(1)
            
        # Check if Docker Compose is available
        try:
            result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Docker Compose found: {result.stdout.strip()}")
            else:
                # Try docker compose (newer version)
                result = subprocess.run(['docker', 'compose', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Docker Compose found: {result.stdout.strip()}")
                else:
                    raise Exception("Docker Compose not found")
        except Exception:
            print("❌ Docker Compose is not available!")
            print("   Please install Docker Desktop which includes Docker Compose")
            sys.exit(1)
            
        # Check if Docker daemon is running
        try:
            result = subprocess.run(['docker', 'ps'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Docker daemon is running")
            else:
                raise Exception("Docker daemon not running")
        except Exception:
            print("❌ Docker daemon is not running!")
            print("   Please start Docker Desktop or Docker service")
            sys.exit(1)
            
    def create_local_env_files(self):
        print("\n📝 Setting up local environment files...")
        
        # Backend .env file
        backend_env = self.project_root / "backend" / ".env"
        backend_env_content = """# Local Development Environment
MONGO_URL=mongodb://admin:thaparmart2024@mongodb:27017/thaparMARTN?authSource=admin
DB_NAME=thaparMARTN
CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://frontend:80

# AWS S3 Configuration (Demo/Test values)
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY
AWS_REGION=ap-south-1
S3_BUCKET_NAME=thaparmart-local

# Razorpay Configuration (Test keys)
RAZORPAY_KEY_ID=rzp_test_RC0rOzm4xN5Drr
RAZORPAY_KEY_SECRET=2wfEhHUe4ZYuPsx7RgaWvGXi
"""
        
        with open(backend_env, 'w') as f:
            f.write(backend_env_content)
        print(f"✅ Created {backend_env}")
        
        # Frontend .env file
        frontend_env = self.project_root / "frontend" / ".env"
        frontend_env_content = """# Frontend Local Environment
REACT_APP_BACKEND_URL=http://localhost:8001
WDS_SOCKET_PORT=443
"""
        
        with open(frontend_env, 'w') as f:
            f.write(frontend_env_content)
        print(f"✅ Created {frontend_env}")
        
    def create_docker_compose_local(self):
        print("\n🐳 Creating Docker Compose configuration...")
        
        compose_content = """version: '3.8'

services:
  # MongoDB Database
  mongodb:
    image: mongo:latest
    container_name: thapar-mongodb-local
    restart: unless-stopped
    ports:
      - "27017:27017"
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: thaparmart2024
      MONGO_INITDB_DATABASE: thaparMARTN
    volumes:
      - mongodb_data_local:/data/db
    networks:
      - thapar-network-local

  # FastAPI Backend
  backend:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    container_name: thapar-backend-local
    restart: unless-stopped
    ports:
      - "8001:8001"
    environment:
      - MONGO_URL=mongodb://admin:thaparmart2024@mongodb:27017/thaparMARTN?authSource=admin
      - DB_NAME=thaparMARTN
      - CORS_ORIGINS=http://localhost:3000,http://localhost:80,http://frontend:80
      - AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
      - AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY
      - AWS_REGION=ap-south-1
      - S3_BUCKET_NAME=thaparmart-local
      - RAZORPAY_KEY_ID=rzp_test_RC0rOzm4xN5Drr
      - RAZORPAY_KEY_SECRET=2wfEhHUe4ZYuPsx7RgaWvGXi
    depends_on:
      - mongodb
    networks:
      - thapar-network-local
    volumes:
      - ./backend:/app
    command: uvicorn server:app --host 0.0.0.0 --port 8001 --reload

  # React Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: thapar-frontend-local
    restart: unless-stopped
    ports:
      - "80:80"
      - "3000:80"
    environment:
      - REACT_APP_BACKEND_URL=http://localhost:8001
    depends_on:
      - backend
    networks:
      - thapar-network-local

volumes:
  mongodb_data_local:

networks:
  thapar-network-local:
    driver: bridge
"""
        
        with open(self.compose_file, 'w') as f:
            f.write(compose_content)
        print(f"✅ Created {self.compose_file}")
        
    def stop_existing_containers(self):
        print("\n🛑 Stopping any existing containers...")
        try:
            subprocess.run(['docker-compose', 'down', '--remove-orphans'], 
                         cwd=self.project_root, check=False)
            print("✅ Stopped existing containers")
        except Exception as e:
            print(f"⚠️  Warning: {e}")
            
    def build_and_start_services(self):
        print("\n🔨 Building and starting services...")
        print("This may take a few minutes on first run...")
        
        try:
            # Build and start services
            result = subprocess.run(['docker-compose', 'up', '--build', '-d'], 
                                  cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Services started successfully!")
            else:
                print(f"❌ Failed to start services:")
                print(result.stderr)
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ Error starting services: {e}")
            sys.exit(1)
            
    def wait_for_services(self):
        print("\n⏳ Waiting for services to be ready...")
        
        for i in range(30):
            try:
                # Check if services are running
                result = subprocess.run(['docker-compose', 'ps'], 
                                      cwd=self.project_root, capture_output=True, text=True)
                
                if "Up" in result.stdout:
                    time.sleep(2)  # Wait a bit more for full startup
                    print("✅ Services are ready!")
                    return True
                    
                time.sleep(2)
                print(f"   Waiting... ({i+1}/30)")
                
            except Exception:
                time.sleep(2)
                
        print("⚠️  Services may still be starting up...")
        return False
        
    def show_service_status(self):
        print("\n📊 Service Status:")
        try:
            result = subprocess.run(['docker-compose', 'ps'], 
                                  cwd=self.project_root, capture_output=True, text=True)
            print(result.stdout)
        except Exception as e:
            print(f"Error getting status: {e}")
            
    def show_access_info(self):
        print("\n🌐 Your Thapar Marketplace is now running!")
        print("=" * 50)
        print("📱 Frontend:      http://localhost")
        print("                 http://localhost:3000")
        print("🔧 Backend API:   http://localhost:8001")
        print("🗄️  Database:     localhost:27017")
        print("=" * 50)
        
        print("\n📋 Useful Commands:")
        print("   View logs:     docker-compose logs -f")
        print("   Stop services: docker-compose down")
        print("   Restart:       python deploy_local.py")
        print("   Backend logs:  docker-compose logs -f backend")
        print("   Frontend logs: docker-compose logs -f frontend")
        
    def run_deployment(self):
        try:
            self.print_banner()
            self.check_prerequisites()
            self.create_local_env_files()
            self.create_docker_compose_local()
            self.stop_existing_containers()
            self.build_and_start_services()
            self.wait_for_services()
            self.show_service_status()
            self.show_access_info()
            
            print("\n🎉 Local deployment completed successfully!")
            print("\n💡 Tip: Your app has hot reload enabled - changes will reflect automatically!")
            
        except KeyboardInterrupt:
            print("\n\n❌ Deployment cancelled by user")
            sys.exit(1)
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    deployment = LocalDeployment()
    deployment.run_deployment()