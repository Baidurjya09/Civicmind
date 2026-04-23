# 🚀 CivicMind — Deployment Guide

Complete guide for deploying CivicMind in production.

## Deployment Options

1. **Local Development** — Run on your machine
2. **Docker** — Containerized deployment
3. **Cloud VM** — AWS/GCP/Azure instance
4. **Kubernetes** — Scalable cluster deployment
5. **Serverless** — AWS Lambda / Cloud Run (API only)

## 1. Local Development

See `QUICK_START.md` for basic setup.

For production-like local deployment:

```bash
# Install as system service (Linux)
sudo cp civicmind.service /etc/systemd/system/
sudo systemctl enable civicmind
sudo systemctl start civicmind

# Or use PM2 (cross-platform)
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

## 2. Docker Deployment

### Single Container

```bash
# Build
docker build -t civicmind:latest .

# Run API
docker run -d \
  --name civicmind-api \
  -p 8080:8080 \
  -v $(pwd)/logs:/app/logs \
  civicmind:latest \
  uvicorn apis.mock_apis:app --host 0.0.0.0 --port 8080

# Run Dashboard
docker run -d \
  --name civicmind-dashboard \
  -p 8501:8501 \
  -v $(pwd)/evaluation:/app/evaluation \
  civicmind:latest \
  streamlit run demo/dashboard.py --server.port 8501 --server.address 0.0.0.0
```

### Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down

# Rebuild after code changes
docker-compose up -d --build
```

### Docker with GPU (for training)

```bash
# Install nvidia-docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update && sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker

# Run training with GPU
docker run --gpus all \
  -v $(pwd)/training:/app/training \
  civicmind:latest \
  python training/train_grpo.py --mode train --epochs 2
```

## 3. Cloud VM Deployment

### AWS EC2

**Instance type:** `g4dn.xlarge` (T4 GPU, $0.526/hour)

```bash
# 1. Launch instance (Ubuntu 22.04 Deep Learning AMI)
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type g4dn.xlarge \
  --key-name your-key \
  --security-group-ids sg-xxxxx

# 2. SSH into instance
ssh -i your-key.pem ubuntu@<instance-ip>

# 3. Clone and setup
git clone https://github.com/YOUR_USERNAME/civicmind.git
cd civicmind
pip install -r requirements.txt

# 4. Run with systemd
sudo cp deployment/civicmind.service /etc/systemd/system/
sudo systemctl enable civicmind
sudo systemctl start civicmind

# 5. Setup nginx reverse proxy
sudo apt install nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/civicmind
sudo ln -s /etc/nginx/sites-available/civicmind /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

### GCP Compute Engine

**Instance type:** `n1-standard-4` + `nvidia-tesla-t4`

```bash
# Create instance with GPU
gcloud compute instances create civicmind-vm \
  --zone=us-central1-a \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --image-family=pytorch-latest-gpu \
  --image-project=deeplearning-platform-release \
  --maintenance-policy=TERMINATE

# SSH and setup
gcloud compute ssh civicmind-vm
# ... same as AWS setup
```

### Azure VM

**Instance type:** `Standard_NC4as_T4_v3` (T4 GPU)

```bash
# Create resource group
az group create --name civicmind-rg --location eastus

# Create VM
az vm create \
  --resource-group civicmind-rg \
  --name civicmind-vm \
  --image UbuntuLTS \
  --size Standard_NC4as_T4_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# SSH and setup
ssh azureuser@<vm-ip>
# ... same as AWS setup
```

## 4. Kubernetes Deployment

### Prerequisites

- Kubernetes cluster (GKE, EKS, AKS, or local minikube)
- kubectl configured
- GPU node pool (for training)

### Deploy

```bash
# Create namespace
kubectl create namespace civicmind

# Deploy API
kubectl apply -f deployment/k8s/api-deployment.yaml
kubectl apply -f deployment/k8s/api-service.yaml

# Deploy Dashboard
kubectl apply -f deployment/k8s/dashboard-deployment.yaml
kubectl apply -f deployment/k8s/dashboard-service.yaml

# Deploy Ingress
kubectl apply -f deployment/k8s/ingress.yaml

# Check status
kubectl get pods -n civicmind
kubectl get services -n civicmind

# View logs
kubectl logs -f deployment/civicmind-api -n civicmind
```

### Autoscaling

```bash
# Horizontal Pod Autoscaler
kubectl apply -f deployment/k8s/hpa.yaml

# Verify
kubectl get hpa -n civicmind
```

## 5. Serverless Deployment

### AWS Lambda (API only)

```bash
# Install Serverless Framework
npm install -g serverless

# Deploy
cd deployment/serverless
serverless deploy --stage prod

# Test
curl https://xxxxx.execute-api.us-east-1.amazonaws.com/prod/city/status
```

### Google Cloud Run

```bash
# Build and push image
gcloud builds submit --tag gcr.io/YOUR_PROJECT/civicmind

# Deploy API
gcloud run deploy civicmind-api \
  --image gcr.io/YOUR_PROJECT/civicmind \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2

# Deploy Dashboard
gcloud run deploy civicmind-dashboard \
  --image gcr.io/YOUR_PROJECT/civicmind \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --command streamlit \
  --args "run,demo/dashboard.py,--server.port,8080"
```

## Production Checklist

### Security

- [ ] Change default ports
- [ ] Enable HTTPS (Let's Encrypt)
- [ ] Set up firewall rules
- [ ] Use environment variables for secrets
- [ ] Enable API authentication
- [ ] Set up CORS properly
- [ ] Regular security updates

### Monitoring

- [ ] Set up logging (CloudWatch, Stackdriver, etc.)
- [ ] Configure alerts (CPU, memory, errors)
- [ ] Add health check endpoints
- [ ] Monitor GPU utilization
- [ ] Track API response times
- [ ] Set up error tracking (Sentry)

### Performance

- [ ] Enable caching (Redis)
- [ ] Use CDN for static assets
- [ ] Optimize Docker image size
- [ ] Configure autoscaling
- [ ] Load balancing (if multi-instance)
- [ ] Database connection pooling

### Backup & Recovery

- [ ] Backup training checkpoints
- [ ] Backup logs and metrics
- [ ] Document recovery procedures
- [ ] Test disaster recovery
- [ ] Version control for configs

## Environment Variables

Create `.env` file:

```bash
# API
API_HOST=0.0.0.0
API_PORT=8080
API_WORKERS=4

# Dashboard
DASHBOARD_PORT=8501

# Training
CUDA_VISIBLE_DEVICES=0
TORCH_CUDA_ARCH_LIST=8.0;8.6;8.9;9.0

# Hugging Face
HF_TOKEN=your_token_here

# Weights & Biases
WANDB_API_KEY=your_key_here
WANDB_PROJECT=civicmind

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/civicmind/app.log

# Security
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

## SSL/HTTPS Setup

### Let's Encrypt (Free)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

### Nginx Config

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location /api/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Cost Optimization

### Cloud GPU Pricing (as of 2025)

| Provider | Instance | GPU | Price/hour | Best For |
|----------|----------|-----|------------|----------|
| AWS | g4dn.xlarge | T4 | $0.526 | Training |
| GCP | n1-standard-4 + T4 | T4 | $0.45 | Training |
| Azure | NC4as_T4_v3 | T4 | $0.526 | Training |
| RunPod | RTX 4090 | 4090 | $0.69 | Fast training |
| Vast.ai | RTX 3090 | 3090 | $0.30 | Budget training |

### Tips

1. **Use spot instances** — 70% cheaper (AWS, GCP, Azure)
2. **Auto-shutdown** — Stop instances when not training
3. **Serverless for API** — Pay per request (Cloud Run, Lambda)
4. **Cache models** — Don't re-download on every deploy
5. **Optimize Docker** — Smaller images = faster deploys

## Troubleshooting

### Port conflicts

```bash
# Find process using port
lsof -i :8080
netstat -tulpn | grep 8080

# Kill process
kill -9 <PID>
```

### Docker issues

```bash
# Clean up
docker system prune -a

# Check logs
docker logs <container-id>

# Restart
docker-compose restart
```

### GPU not detected

```bash
# Check NVIDIA driver
nvidia-smi

# Check Docker GPU access
docker run --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## Support

For deployment issues:
- Check logs: `docker-compose logs -f`
- Open issue on GitHub
- See main README.md for more info
