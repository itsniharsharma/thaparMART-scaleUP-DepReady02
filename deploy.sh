#!/bin/bash

# Thapar Marketplace Deployment Script
# Usage: ./deploy.sh [local|production]

set -e

ENVIRONMENT=${1:-local}

echo "🚀 Starting deployment for: $ENVIRONMENT"

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        echo "❌ Docker is not running. Please start Docker first."
        exit 1
    fi
    echo "✅ Docker is running"
}

# Function to check if required files exist
check_files() {
    local files=("docker-compose.yml" "backend/Dockerfile" "frontend/Dockerfile")
    
    for file in "${files[@]}"; do
        if [ ! -f "$file" ]; then
            echo "❌ Required file missing: $file"
            exit 1
        fi
    done
    echo "✅ All required files present"
}

# Function for local deployment
deploy_local() {
    echo "🏠 Deploying locally..."
    
    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose down --remove-orphans || true
    
    # Build and start services
    echo "🔨 Building and starting services..."
    docker-compose up --build -d
    
    echo "⏳ Waiting for services to start..."
    sleep 10
    
    # Check service health
    echo "🔍 Checking service health..."
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services are running!"
        echo ""
        echo "🌐 Your application is available at:"
        echo "   Frontend: http://localhost"
        echo "   Backend API: http://localhost:8001"
        echo "   MongoDB: localhost:27017"
        echo ""
        echo "📋 View logs with: docker-compose logs -f"
        echo "🛑 Stop with: docker-compose down"
    else
        echo "❌ Some services failed to start. Check logs:"
        docker-compose logs
        exit 1
    fi
}

# Function for production deployment
deploy_production() {
    echo "🏭 Deploying for production..."
    
    # Check if production env file exists
    if [ ! -f ".env.production" ]; then
        echo "❌ .env.production file not found!"
        echo "   Please create .env.production with your actual credentials"
        exit 1
    fi
    
    # Load production environment
    export $(cat .env.production | xargs)
    
    # Stop existing containers
    echo "🛑 Stopping existing containers..."
    docker-compose -f docker-compose.prod.yml down --remove-orphans || true
    
    # Build and start services
    echo "🔨 Building and starting production services..."
    docker-compose -f docker-compose.prod.yml up --build -d
    
    echo "⏳ Waiting for services to start..."
    sleep 15
    
    # Check service health
    echo "🔍 Checking service health..."
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo "✅ Production services are running!"
        echo ""
        echo "🌐 Your application should be available at your configured domain"
        echo ""
        echo "📋 View logs with: docker-compose -f docker-compose.prod.yml logs -f"
        echo "🛑 Stop with: docker-compose -f docker-compose.prod.yml down"
    else
        echo "❌ Some services failed to start. Check logs:"
        docker-compose -f docker-compose.prod.yml logs
        exit 1
    fi
}

# Main deployment logic
main() {
    echo "🔍 Checking prerequisites..."
    check_docker
    check_files
    
    case $ENVIRONMENT in
        "local")
            deploy_local
            ;;
        "production")
            deploy_production
            ;;
        *)
            echo "❌ Invalid environment: $ENVIRONMENT"
            echo "Usage: ./deploy.sh [local|production]"
            exit 1
            ;;
    esac
    
    echo ""
    echo "🎉 Deployment completed successfully!"
}

# Run main function
main