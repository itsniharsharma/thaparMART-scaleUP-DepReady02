# 🚀 Thapar Marketplace - Simple Deployment Commands

## Prerequisites
Make sure you have Python 3.6+ installed and Docker running on your system.

## 📋 Installation Commands

### 1. Install Docker (if not already installed)

**Windows:**
```bash
# Download and install Docker Desktop from https://docker.com
# Or use Windows Package Manager
winget install Docker.DockerDesktop
```

**macOS:**
```bash
# Download and install Docker Desktop from https://docker.com
# Or use Homebrew
brew install --cask docker
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
# Logout and login again
```

### 2. Navigate to Your Project
```bash
cd /path/to/your/thapar-marketplace
```

## 🏠 LOCAL DEPLOYMENT

### Single Command to Deploy Locally:
```bash
python deploy_local.py
```

**That's it!** This command will:
- ✅ Check all prerequisites
- ✅ Create all necessary configuration files
- ✅ Set up Docker containers
- ✅ Start your application
- ✅ Show you access URLs

**Your app will be available at:**
- Frontend: http://localhost
- Backend: http://localhost:8001

## 🏭 PRODUCTION DEPLOYMENT

### Single Command to Deploy to Production:
```bash
python deploy_production.py
```

**This command will:**
- ✅ Check prerequisites
- ✅ Ask for your production configuration (APIs keys, domain, etc.)
- ✅ Create production-ready Docker setup
- ✅ Deploy your application
- ✅ Set up backup scripts

## 📱 Quick Commands Reference

| Task | Command |
|------|---------|
| **Deploy Locally** | `python deploy_local.py` |
| **Deploy Production** | `python deploy_production.py` |
| **View Logs** | `docker-compose logs -f` |
| **Stop Local** | `docker-compose down` |
| **Stop Production** | `docker-compose -f docker-compose.prod.yml down` |
| **Backup Database** | `python backup_production.py` |

## 🔧 Manual Commands (if needed)

### Local Development:
```bash
# Start local services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production:
```bash
# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f

# Stop production services
docker-compose -f docker-compose.prod.yml down
```

## 🌐 Access Your Application

### Local Development:
- **Frontend**: http://localhost or http://localhost:3000
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

### Production:
- **Frontend**: Your configured domain (https://your-domain.com)
- **Backend API**: Your configured API domain
- **Database**: Internal (not exposed to public)

## 🔄 Automatic Updates

To set up automatic deployment when you make changes:

### Option 1: Use Emergent Platform (Easiest)
1. Click "Deploy" in Emergent interface
2. Use "Save to GitHub" to push changes
3. Changes automatically reflect in deployment

### Option 2: GitHub Actions
1. Push your code to GitHub
2. The included `.github/workflows/deploy.yml` will handle automatic deployment

### Option 3: Manual Re-deployment
```bash
# For local changes
python deploy_local.py

# For production updates
python deploy_production.py
```

## 🆘 Troubleshooting

### If something goes wrong:

1. **Check Docker is running:**
   ```bash
   docker --version
   docker ps
   ```

2. **View detailed logs:**
   ```bash
   docker-compose logs
   ```

3. **Reset everything:**
   ```bash
   docker-compose down -v
   python deploy_local.py
   ```

4. **Check port conflicts:**
   ```bash
   # On Windows
   netstat -ano | findstr :80
   netstat -ano | findstr :8001
   
   # On Mac/Linux
   lsof -i :80
   lsof -i :8001
   ```

## 📞 Support

If you encounter any issues:
1. Make sure Docker is running
2. Check that ports 80 and 8001 are not in use
3. Verify your internet connection for downloading images
4. Check the logs for specific error messages

## 🎯 What Each Script Does

### `deploy_local.py`:
- Sets up development environment
- Uses test API keys
- Enables hot reload for development
- Exposes database for debugging
- Creates local Docker network

### `deploy_production.py`:
- Asks for your real API keys
- Sets up production-optimized containers
- Configures proper security settings
- Creates backup procedures
- Uses production-grade configurations

## 🔐 Security Notes

- Never commit production API keys to version control
- Use strong passwords for production database
- Set up SSL certificates for HTTPS in production
- Configure firewall rules appropriately
- Regular backups are created automatically

---

**Ready to deploy? Just run:**
```bash
python deploy_local.py
```