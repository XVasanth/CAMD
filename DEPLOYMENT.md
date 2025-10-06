# 📚 CAD Assessment System - Deployment Guide

## Table of Contents
1. [Local Development](#local-development)
2. [Production Deployment](#production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Microsoft 365 Integration](#microsoft-365-integration)
6. [Security Considerations](#security-considerations)

## 🏠 Local Development

### Quick Start
```bash
# Clone repository
git clone https://github.com/yourusername/cad-assessment-system.git
cd cad-assessment-system

# Run setup script
python setup.py

# Or manually:
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run application
streamlit run app.py
```

### Development Settings
Create `.streamlit/secrets.toml` for local configuration:
```toml
[general]
debug = true
max_upload_size = 500

[paths]
models_dir = "./sample_models"
reports_dir = "./reports"
```

## 🚀 Production Deployment

### System Requirements
- **OS:** Ubuntu 20.04+ / Windows Server 2019+ / macOS 11+
- **Python:** 3.8 or higher
- **RAM:** Minimum 4GB (8GB recommended)
- **Storage:** 10GB minimum
- **CPU:** 2+ cores recommended

### Linux Server Deployment

#### 1. System Setup
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.10 python3.10-venv python3-pip nginx supervisor -y

# Install system libraries for mesh processing
sudo apt install libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev -y
```

#### 2. Application Setup
```bash
# Create application directory
sudo mkdir -p /opt/cad-assessment
cd /opt/cad-assessment

# Clone repository
sudo git clone https://github.com/yourusername/cad-assessment-system.git .

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Systemd Service
Create `/etc/systemd/system/cad-assessment.service`:
```ini
[Unit]
Description=CAD Assessment System
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/cad-assessment
Environment="PATH=/opt/cad-assessment/venv/bin"
ExecStart=/opt/cad-assessment/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cad-assessment
sudo systemctl start cad-assessment
```

#### 4. Nginx Reverse Proxy
Create `/etc/nginx/sites-available/cad-assessment`:
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/cad-assessment /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### Windows Server Deployment

#### 1. IIS Setup with HTTP Platform Handler
```powershell
# Install IIS and required features
Enable-WindowsFeature -Name Web-Server, Web-Common-Http, Web-Http-Redirect, Web-Asp-Net45

# Install HTTP Platform Handler
# Download from: https://www.iis.net/downloads/microsoft/httpplatformhandler
```

#### 2. Application Setup
```powershell
# Create directory
New-Item -ItemType Directory -Path "C:\inetpub\cad-assessment"
Set-Location "C:\inetpub\cad-assessment"

# Clone repository
git clone https://github.com/yourusername/cad-assessment-system.git .

# Setup Python environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

#### 3. IIS Configuration
Create `web.config`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <system.webServer>
        <handlers>
            <add name="httpPlatformHandler" path="*" verb="*" 
                 modules="httpPlatformHandler" resourceType="Unspecified" />
        </handlers>
        <httpPlatform processPath="C:\inetpub\cad-assessment\venv\Scripts\python.exe"
                      arguments="C:\inetpub\cad-assessment\venv\Scripts\streamlit run app.py --server.port %HTTP_PLATFORM_PORT%"
                      stdoutLogEnabled="true"
                      stdoutLogFile=".\logs\python.log"
                      startupTimeLimit="60">
            <environmentVariables>
                <environmentVariable name="SERVER_PORT" value="%HTTP_PLATFORM_PORT%" />
            </environmentVariables>
        </httpPlatform>
    </system.webServer>
</configuration>
```

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker build -t cad-assessment .

# Run container
docker run -d \
  --name cad-assessment \
  -p 8501:8501 \
  -v $(pwd)/sample_models:/app/sample_models \
  -v $(pwd)/reports:/app/reports \
  cad-assessment

# Or use docker-compose
docker-compose up -d
```

### Docker Swarm Deployment
```bash
# Initialize swarm
docker swarm init

# Deploy stack
docker stack deploy -c docker-compose.yml cad-assessment-stack

# Scale service
docker service scale cad-assessment-stack_cad-assessment=3
```

### Kubernetes Deployment
Create `k8s-deployment.yaml`:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cad-assessment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cad-assessment
  template:
    metadata:
      labels:
        app: cad-assessment
    spec:
      containers:
      - name: cad-assessment
        image: yourusername/cad-assessment:latest
        ports:
        - containerPort: 8501
        volumeMounts:
        - name: models
          mountPath: /app/sample_models
        - name: reports
          mountPath: /app/reports
      volumes:
      - name: models
        persistentVolumeClaim:
          claimName: models-pvc
      - name: reports
        persistentVolumeClaim:
          claimName: reports-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: cad-assessment-service
spec:
  selector:
    app: cad-assessment
  ports:
  - port: 80
    targetPort: 8501
  type: LoadBalancer
```

Deploy to Kubernetes:
```bash
kubectl apply -f k8s-deployment.yaml
```

## ☁️ Cloud Deployment

### AWS EC2 Deployment
```bash
# Launch EC2 instance (Ubuntu 20.04)
# Open ports: 22 (SSH), 80 (HTTP), 443 (HTTPS), 8501 (Streamlit)

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow Linux Server Deployment steps above
```

### Azure App Service
```bash
# Create resource group
az group create --name cad-assessment-rg --location eastus

# Create App Service plan
az appservice plan create \
  --name cad-assessment-plan \
  --resource-group cad-assessment-rg \
  --sku B1 --is-linux

# Create web app
az webapp create \
  --resource-group cad-assessment-rg \
  --plan cad-assessment-plan \
  --name cad-assessment-app \
  --runtime "PYTHON|3.10"

# Deploy code
az webapp up \
  --resource-group cad-assessment-rg \
  --name cad-assessment-app
```

### Google Cloud Run
```bash
# Build and push to Container Registry
gcloud builds submit --tag gcr.io/PROJECT-ID/cad-assessment

# Deploy to Cloud Run
gcloud run deploy cad-assessment \
  --image gcr.io/PROJECT-ID/cad-assessment \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Heroku Deployment
Create `Procfile`:
```
web: streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

Deploy:
```bash
heroku create cad-assessment-app
git push heroku main
heroku open
```

## 🔗 Microsoft 365 Integration

### SharePoint Integration
```python
# Add to app.py for SharePoint integration
from sharepoint import SharePointSite, Site

def upload_to_sharepoint(file_path, site_url, folder_path):
    site = Site(site_url, auth=your_auth)
    folder = site.Folder(folder_path)
    with open(file_path, 'rb') as f:
        folder.upload_file(f, os.path.basename(file_path))
```

### Teams Integration
Configure webhook for notifications:
```python
import requests

def send_teams_notification(webhook_url, message):
    payload = {
        "text": message,
        "title": "CAD Assessment Update"
    }
    requests.post(webhook_url, json=payload)
```

### Power Automate Flow
1. Create flow triggered on file upload to SharePoint
2. Call CAD Assessment API endpoint
3. Save results back to SharePoint
4. Notify via Teams/Email

## 🔒 Security Considerations

### SSL/TLS Configuration
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

### Environment Variables
Create `.env` file (never commit to Git):
```
SECRET_KEY=your-secret-key
DATABASE_URL=your-db-url
MAX_UPLOAD_SIZE=200
ALLOWED_HOSTS=your-domain.com
```

### Security Headers
Add to Nginx configuration:
```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

### User Authentication
For production, implement authentication:
```python
# Add to app.py
import streamlit_authenticator as stauth

authenticator = stauth.Authenticate(
    names=['Admin', 'Teacher'],
    usernames=['admin', 'teacher'],
    passwords=['hashed_password_1', 'hashed_password_2'],
    cookie_name='cad_assessment_cookie',
    key='random_key',
    cookie_expiry_days=30
)

name, authentication_status, username = authenticator.login('Login', 'main')
```

## 📊 Monitoring

### Application Monitoring
```python
# Add logging
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Health Check Endpoint
```python
@st.cache_data
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Performance Monitoring
- Use Prometheus + Grafana for metrics
- Set up alerts for high CPU/memory usage
- Monitor file upload sizes and processing times

## 🔄 Updates and Maintenance

### Update Procedure
```bash
# Backup current version
tar -czf backup-$(date +%Y%m%d).tar.gz /opt/cad-assessment

# Pull latest changes
cd /opt/cad-assessment
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Restart service
sudo systemctl restart cad-assessment
```

### Database Backup (if using)
```bash
# Daily backup cron job
0 2 * * * pg_dump cad_assessment > /backups/cad_assessment_$(date +\%Y\%m\%d).sql
```

## 📧 Support

For deployment issues:
1. Check logs: `journalctl -u cad-assessment -f`
2. Verify dependencies: `pip list`
3. Test locally first
4. Open GitHub issue with error details

---

**Note:** Always test in a staging environment before deploying to production.
