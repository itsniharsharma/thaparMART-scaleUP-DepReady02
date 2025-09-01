# Thapar University Marketplace - Docker Deployment Guide

This guide will help you deploy your Thapar University marketplace application using Docker and set up automatic deployment.

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Git (for version control)
- Your actual API keys (AWS S3, Razorpay)

### 1. Local Development Deployment

```bash
# Make the deployment script executable
chmod +x deploy.sh

# Deploy locally
./deploy.sh local
```

Your application will be available at:
- **Frontend**: http://localhost
- **Backend API**: http://localhost:8001
- **Database**: MongoDB running on localhost:27017

### 2. Production Deployment

```bash
# Copy and configure production environment
cp .env.production .env.production.local
# Edit .env.production.local with your actual values

# Deploy to production
./deploy.sh production
```

## 📋 Configuration

### Environment Variables

#### Development (.env files already configured)
- Backend: `/backend/.env`
- Frontend: `/frontend/.env`

#### Production (.env.production)
```bash
# Update these with your actual values:
MONGO_PASSWORD=your_secure_password
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://your-domain.com
AWS_ACCESS_KEY_ID=your_actual_key
AWS_SECRET_ACCESS_KEY=your_actual_secret
S3_BUCKET_NAME=your_bucket
RAZORPAY_KEY_ID=your_key
RAZORPAY_KEY_SECRET=your_secret
```

## 🔧 Manual Docker Commands

### Development Commands
```bash
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Restart specific service
docker-compose restart backend

# View running containers
docker ps
```

### Production Commands
```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up --build -d

# Production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production
docker-compose -f docker-compose.prod.yml down
```

## 🚀 Deployment Options

### Option 1: Local Server/VPS Deployment

1. **Setup Server** (Ubuntu/CentOS)
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. **Clone and Deploy**
```bash
git clone https://github.com/yourusername/thapar-marketplace.git
cd thapar-marketplace
./deploy.sh production
```

### Option 2: Cloud Deployment

#### AWS EC2
```bash
# Launch EC2 instance with Ubuntu
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow local server setup steps above
```

#### DigitalOcean
```bash
# Create droplet with Docker marketplace image
# SSH and deploy
ssh root@your-droplet-ip
# Follow deployment steps
```

### Option 3: Using Emergent Platform

Since you're already on Emergent, the easiest option:

1. Click the **"Deploy"** button in Emergent interface
2. This creates a production environment (50 credits/month)
3. Get a public URL automatically
4. Use "Save to GitHub" for version control

## 🔄 Automatic Deployment Setup

### Option 1: GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy Thapar Marketplace

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/thapar-marketplace
          git pull origin main
          ./deploy.sh production
```

### Option 2: Webhook Auto-Deploy

1. **Setup Webhook Script**
```bash
# Make auto-deploy script executable
chmod +x scripts/auto-deploy.sh
```

2. **Configure Webhook URL** in GitHub repository settings
3. **Point webhook to your server endpoint** that triggers the script

### Option 3: Simple Git Hook

```bash
# On your server, create a git hook
cd /path/to/your/repo/.git/hooks
nano post-receive

# Add this content:
#!/bin/bash
cd /path/to/thapar-marketplace
./deploy.sh production
```

## 📊 Monitoring & Maintenance

### View Application Status
```bash
# Check running services
docker ps

# Monitor resource usage
docker stats

# View specific service logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

### Database Backup
```bash
# Manual backup
docker exec thapar-mongodb mongodump --out /backup
docker cp thapar-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)

# Restore from backup
docker cp ./mongodb-backup thapar-mongodb:/restore
docker exec thapar-mongodb mongorestore /restore
```

### Health Checks
```bash
# Test backend API
curl http://localhost:8001/api/products

# Test frontend
curl http://localhost

# Check database connection
docker exec thapar-mongodb mongo --eval "db.stats()"
```

## 🔒 Security Considerations

1. **Use strong passwords** for MongoDB
2. **Configure firewall** rules (only allow necessary ports)
3. **Use HTTPS** in production (add SSL certificates)
4. **Keep Docker images updated**
5. **Backup regularly**

## 🆘 Troubleshooting

### Common Issues

1. **Services won't start**
```bash
# Check logs
docker-compose logs

# Check if ports are in use
netstat -tulpn | grep :80
netstat -tulpn | grep :8001
```

2. **Database connection issues**
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Test connection
docker exec thapar-mongodb mongo --eval "db.stats()"
```

3. **Frontend can't reach backend**
```bash
# Check network connectivity
docker network ls
docker network inspect thapar-marketplace_thapar-network
```

### Reset Everything
```bash
# Stop all services
docker-compose down

# Remove all data (WARNING: This deletes your database!)
docker-compose down -v

# Remove all images
docker system prune -a

# Start fresh
./deploy.sh local
```

## 📞 Support

For deployment issues or questions:
1. Check the logs first: `docker-compose logs`
2. Verify your environment variables
3. Ensure all ports are available
4. Check firewall settings

## 🎯 Next Steps

1. **Domain Setup**: Configure your domain to point to your server
2. **SSL Certificate**: Set up HTTPS with Let's Encrypt
3. **Monitoring**: Add monitoring tools like Grafana
4. **Scaling**: Consider Docker Swarm or Kubernetes for scaling
5. **CDN**: Use CloudFlare or similar for better performance

Your Thapar University marketplace is now ready for the world! 🌍