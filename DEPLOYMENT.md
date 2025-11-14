# Deployment Guide

This guide covers deploying the Market Intelligence Chatbot to various cloud platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Cloud Platforms](#cloud-platforms)
  - [Railway](#railway)
  - [Render](#render)
  - [AWS ECS](#aws-ecs)
  - [Google Cloud Run](#google-cloud-run)
  - [DigitalOcean](#digitalocean)
- [Environment Variables](#environment-variables)
- [Monitoring](#monitoring)
- [Scaling](#scaling)

## Prerequisites

Before deploying, ensure you have:

1. ✅ Groq API key
2. ✅ NewsAPI key
3. ✅ Upstash Redis instance
4. ✅ Docker installed (for containerized deployments)
5. ✅ Cloud platform account (if deploying to cloud)

## Docker Deployment

### Using Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd mcp-chatbot
   ```

2. **Create environment file**
   ```bash
   cp .env.template .env
   # Edit .env with your actual credentials
   ```

3. **Build and run**
   ```bash
   docker-compose up -d
   ```

4. **Check status**
   ```bash
   docker-compose ps
   docker-compose logs -f
   ```

5. **Access the application**
   - Chatbot API: http://localhost:8080
   - MCP Server: http://localhost:8000

### Manual Docker Deployment

**MCP Server:**
```bash
docker build -t mcp-server .
docker run -d \
  -p 8000:8000 \
  -e NEWS_API_KEY=your_key \
  --name mcp-server \
  mcp-server
```

**Chatbot Backend:**
```bash
cd chatbot-backend
docker build -t chatbot-backend .
docker run -d \
  -p 8080:8080 \
  -e GROQ_API_KEY=your_key \
  -e MCP_SERVER_URL=http://mcp-server:8000/mcp \
  -e UPSTASH_REDIS_REST_URL=your_url \
  -e UPSTASH_REDIS_REST_TOKEN=your_token \
  --link mcp-server:mcp-server \
  --name chatbot-backend \
  chatbot-backend
```

## Cloud Platforms

### Railway

Railway is excellent for quick deployments with Git integration.

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Create new project**
   ```bash
   railway init
   ```

3. **Deploy MCP Server**
   ```bash
   railway up
   railway variables set NEWS_API_KEY=your_key
   ```

4. **Deploy Chatbot Backend**
   ```bash
   cd chatbot-backend
   railway up
   railway variables set GROQ_API_KEY=your_key
   railway variables set MCP_SERVER_URL=https://your-mcp-server.railway.app/mcp
   railway variables set UPSTASH_REDIS_REST_URL=your_url
   railway variables set UPSTASH_REDIS_REST_TOKEN=your_token
   ```

5. **Link services**
   - In Railway dashboard, use service linking for internal communication

### Render

Render provides free tier with automatic deploys from Git.

1. **Create new Web Service**
   - Go to [Render Dashboard](https://dashboard.render.com)
   - Click "New +" → "Web Service"
   - Connect your repository

2. **Configure MCP Server**
   - Name: `mcp-server`
   - Runtime: `Docker`
   - Dockerfile path: `./Dockerfile`
   - Add environment variables

3. **Configure Chatbot Backend**
   - Name: `chatbot-backend`
   - Runtime: `Docker`
   - Dockerfile path: `./chatbot-backend/Dockerfile`
   - Add environment variables

4. **Environment Variables**
   - Set all required variables in Render dashboard
   - Use internal URLs for service-to-service communication

### AWS ECS (Elastic Container Service)

1. **Create ECR repositories**
   ```bash
   aws ecr create-repository --repository-name mcp-server
   aws ecr create-repository --repository-name chatbot-backend
   ```

2. **Build and push images**
   ```bash
   # Login to ECR
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

   # Build and push MCP server
   docker build -t mcp-server .
   docker tag mcp-server:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/mcp-server:latest

   # Build and push chatbot backend
   cd chatbot-backend
   docker build -t chatbot-backend .
   docker tag chatbot-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/chatbot-backend:latest
   ```

3. **Create ECS cluster**
   ```bash
   aws ecs create-cluster --cluster-name mcp-chatbot-cluster
   ```

4. **Create task definitions**
   - Create task definition JSON files for both services
   - Include environment variables and secrets

5. **Create services**
   ```bash
   aws ecs create-service \
     --cluster mcp-chatbot-cluster \
     --service-name mcp-server \
     --task-definition mcp-server:1 \
     --desired-count 1 \
     --launch-type FARGATE
   ```

### Google Cloud Run

1. **Enable Cloud Run API**
   ```bash
   gcloud services enable run.googleapis.com
   ```

2. **Build and deploy MCP Server**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/mcp-server
   gcloud run deploy mcp-server \
     --image gcr.io/PROJECT_ID/mcp-server \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars NEWS_API_KEY=your_key
   ```

3. **Build and deploy Chatbot Backend**
   ```bash
   cd chatbot-backend
   gcloud builds submit --tag gcr.io/PROJECT_ID/chatbot-backend
   gcloud run deploy chatbot-backend \
     --image gcr.io/PROJECT_ID/chatbot-backend \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GROQ_API_KEY=your_key,MCP_SERVER_URL=https://mcp-server-xxx.run.app/mcp
   ```

### DigitalOcean

1. **Install doctl**
   ```bash
   snap install doctl
   doctl auth init
   ```

2. **Create App Platform app**
   ```bash
   doctl apps create --spec app-spec.yaml
   ```

3. **Create app-spec.yaml**
   ```yaml
   name: mcp-chatbot
   services:
   - name: mcp-server
     dockerfile_path: Dockerfile
     source_dir: /
     github:
       repo: your-username/mcp-chatbot
       branch: main
     http_port: 8000
     envs:
     - key: NEWS_API_KEY
       value: your_key
       
   - name: chatbot-backend
     dockerfile_path: Dockerfile
     source_dir: /chatbot-backend
     github:
       repo: your-username/mcp-chatbot
       branch: main
     http_port: 8080
     envs:
     - key: GROQ_API_KEY
       value: your_key
     - key: MCP_SERVER_URL
       value: ${mcp-server.PUBLIC_URL}/mcp
   ```

## Environment Variables

### Required Variables

**MCP Server:**
- `NEWS_API_KEY` - Your NewsAPI key

**Chatbot Backend:**
- `GROQ_API_KEY` - Your Groq API key
- `MCP_SERVER_URL` - URL to MCP server (e.g., http://mcp-server:8000/mcp)
- `UPSTASH_REDIS_REST_URL` - Upstash Redis URL
- `UPSTASH_REDIS_REST_TOKEN` - Upstash Redis token

### Optional Variables

- `GROQ_MODEL` - Groq model to use (default: llama3-8b-8192)
- `LOG_LEVEL` - Logging level (default: INFO)
- `PORT` - Server port (default: 8080 for chatbot, 8000 for MCP server)
- `MCP_TRANSPORT_PROTOCOL` - "http" or "stdio" (default: http)

## Monitoring

### Health Checks

Both services expose health endpoints:

- MCP Server: `GET /health`
- Chatbot Backend: `GET /health`

### Logging

Access logs from your deployment platform:

**Docker Compose:**
```bash
docker-compose logs -f [service-name]
```

**Railway:**
```bash
railway logs
```

**Render:**
- View logs in the Render dashboard

**AWS CloudWatch:**
```bash
aws logs tail /ecs/mcp-server --follow
```

### Metrics to Monitor

- Request rate
- Response time
- Error rate
- Token usage (Groq API)
- Cache hit rate (Redis)
- Rate limit violations

## Scaling

### Horizontal Scaling

**Docker Compose:**
```bash
docker-compose up -d --scale chatbot-backend=3
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: chatbot-backend
spec:
  replicas: 3
  # ... rest of config
```

### Vertical Scaling

Increase container resources:

**Docker:**
```bash
docker run --memory="2g" --cpus="2" chatbot-backend
```

**Cloud platforms:**
- Adjust instance size in platform dashboard

### Auto-scaling

**AWS ECS:**
```bash
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/mcp-chatbot-cluster/chatbot-backend \
  --min-capacity 1 \
  --max-capacity 10
```

**Google Cloud Run:**
- Automatically scales based on traffic
- Configure max instances in deployment

## Troubleshooting

### Common Issues

1. **MCP Server connection failed**
   - Check MCP_SERVER_URL is correct
   - Verify network connectivity between services
   - Check firewall rules

2. **Redis connection issues**
   - Verify Upstash credentials
   - Check network access to Upstash
   - App will continue without Redis (features disabled)

3. **Groq API errors**
   - Check API key validity
   - Verify rate limits
   - Monitor API quota

4. **Out of memory**
   - Increase container memory limits
   - Check for memory leaks in logs
   - Scale horizontally

### Getting Help

- Check application logs
- Review health check endpoints
- Open an issue on GitHub
- Check cloud platform status pages

## Security Best Practices

1. **Environment Variables**
   - Never commit `.env` files
   - Use secrets management (AWS Secrets Manager, etc.)
   - Rotate keys regularly

2. **Network Security**
   - Use HTTPS in production
   - Implement API authentication
   - Use VPC/private networks for inter-service communication

3. **Rate Limiting**
   - Monitor rate limit violations
   - Adjust limits based on usage
   - Implement user authentication for higher limits

4. **Monitoring**
   - Set up alerts for errors
   - Monitor unusual traffic patterns
   - Track API usage and costs

## Cost Optimization

1. **Caching**
   - Redis caching reduces API calls
   - Configure appropriate TTLs

2. **Auto-scaling**
   - Scale down during low traffic
   - Use serverless for sporadic workloads

3. **API Usage**
   - Monitor Groq API usage
   - Use caching effectively
   - Implement request throttling

4. **Infrastructure**
   - Use free tiers where available
   - Right-size instances
   - Use spot instances (AWS) for non-critical workloads

