#!/bin/bash

# Auto-deployment script for continuous deployment
# This script can be triggered by webhooks or CI/CD pipelines

set -e

PROJECT_DIR="/path/to/your/thapar-marketplace"
BACKUP_DIR="/path/to/backups"
LOG_FILE="/var/log/thapar-autodeploy.log"

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Function to create backup
create_backup() {
    log "Creating backup..."
    
    # Create backup directory if it doesn't exist
    mkdir -p "$BACKUP_DIR"
    
    # Backup MongoDB data
    docker exec thapar-mongodb-prod mongodump --out /backup
    docker cp thapar-mongodb-prod:/backup "$BACKUP_DIR/mongo-$(date +%Y%m%d-%H%M%S)"
    
    log "Backup created successfully"
}

# Function to deploy
deploy() {
    log "Starting auto-deployment..."
    
    cd "$PROJECT_DIR"
    
    # Pull latest changes
    log "Pulling latest changes from git..."
    git pull origin main
    
    # Create backup before deployment
    create_backup
    
    # Deploy production
    log "Deploying production services..."
    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up --build -d
    
    # Wait for services to be ready
    log "Waiting for services to start..."
    sleep 30
    
    # Health check
    if docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        log "✅ Auto-deployment completed successfully!"
        
        # Send notification (optional)
        # curl -X POST "https://your-webhook-url.com/notify" \
        #      -H "Content-Type: application/json" \
        #      -d '{"message": "Thapar Marketplace deployed successfully"}'
        
    else
        log "❌ Deployment failed! Rolling back..."
        
        # Rollback logic (optional)
        # docker-compose -f docker-compose.prod.yml down
        # docker-compose -f docker-compose.prod.yml up -d
        
        exit 1
    fi
}

# Main execution
main() {
    log "Auto-deployment triggered"
    deploy
    log "Auto-deployment process completed"
}

# Run with error handling
if ! main; then
    log "❌ Auto-deployment failed!"
    exit 1
fi