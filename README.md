# Video to MP3 Converter - Microservices Architecture

A distributed microservices application that converts video files to MP3 format, built with Python, deployed on Kubernetes (Minikube), and featuring a modern Streamlit web interface.

## 🎯 Features

- 🔐 JWT-based authentication
- 📤 Video file upload (MP4, AVI, MOV, MKV)
- 🎵 Automatic video-to-MP3 conversion
- 📥 MP3 file download
- 🎨 Modern, responsive web UI
- ⚡ Asynchronous processing with RabbitMQ
- 📦 Horizontally scalable converter service
- 🗄️ GridFS for large file storage

## 🏗️ Architecture

```
Streamlit UI → Gateway Service → Auth Service → PostgreSQL
                    ↓
              MongoDB (Videos/MP3s)
                    ↓
              RabbitMQ → Converter Service (4 replicas)
```

### Services:
- **Gateway Service** - API gateway, handles file uploads/downloads
- **Auth Service** - User authentication with JWT tokens
- **Converter Service** - Video to MP3 conversion (scalable)
- **PostgreSQL** - User authentication database
- **MongoDB** - Video and MP3 file storage (GridFS)
- **RabbitMQ** - Message queue for async processing
- **Streamlit UI** - Web interface for users

---

## 📋 Prerequisites

Install the following before deploying:

```bash
# Homebrew (macOS package manager)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Docker Desktop
brew install --cask docker
# Start Docker Desktop from Applications

# Minikube
brew install minikube

# kubectl
brew install kubectl

# Python 3 (usually pre-installed)
python3 --version
```

Verify installations:
```bash
minikube version
docker --version
kubectl version --client
python3 --version
```

---

## 🚀 Deployment Steps

### Step 1: Start Minikube

```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube status
```

---

### Step 2: Configure Docker Environment

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)
```

---

### Step 3: Build Docker Images

```bash
cd ~/Desktop/microservices-python-app
./build-images.sh
```

**Wait for build to complete (~5-10 minutes)**

This builds images for:
- auth-service
- gateway-service  
- converter-service

---

### Step 4: Deploy Databases

```bash
# Deploy PostgreSQL
kubectl apply -f manifests/postgres.yaml

# Deploy MongoDB
kubectl apply -f manifests/mongodb.yaml

# Deploy RabbitMQ
kubectl apply -f manifests/rabbitmq.yaml

# Wait for databases to be ready
kubectl get pods -w
```

**Press Ctrl+C when all 3 database pods show "Running" and "1/1"**

Expected output:
```
postgres-xxxxx        1/1     Running   0          30s
mongodb-0             1/1     Running   0          30s
rabbitmq-xxxxx        1/1     Running   0          30s
```

---

### Step 5: Setup RabbitMQ Queues

```bash
./setup-rabbitmq-queues.sh
```

This creates two queues:
- `video` - for conversion jobs
- `mp3` - for completed conversions

---

### Step 6: Deploy Auth Service

```bash
kubectl apply -f src/auth-service/manifest/configmap.yaml
kubectl apply -f src/auth-service/manifest/secret.yaml
kubectl apply -f src/auth-service/manifest/service.yaml
kubectl apply -f src/auth-service/manifest/deployment.yaml
```

---

### Step 7: Deploy Gateway Service

```bash
kubectl apply -f src/gateway-service/manifest/configmap.yaml
kubectl apply -f src/gateway-service/manifest/secret.yaml
kubectl apply -f src/gateway-service/manifest/service.yaml
kubectl apply -f src/gateway-service/manifest/gateway-deploy.yaml
```

---

### Step 8: Deploy Converter Service

```bash
kubectl apply -f src/converter-service/manifest/configmap.yaml
kubectl apply -f src/converter-service/manifest/secret.yaml
kubectl apply -f src/converter-service/manifest/converter-deploy.yaml
```

---

### Step 9: Verify All Pods Running

```bash
kubectl get pods
```

**Expected: All pods showing "Running" status**

You should see approximately 11 pods:
- postgres (1)
- mongodb (1)
- rabbitmq (1)
- auth (2 replicas)
- gateway (2 replicas)
- converter (4 replicas)

---

### Step 10: Install Streamlit Dependencies

```bash
cd streamlit-app
pip3 install -r requirements.txt
```

---

### Step 11: Run the Application

You need **two terminal windows**:

**Terminal 1 - Port Forward Gateway Service:**
```bash
cd ~/Desktop/microservices-python-app/streamlit-app
kubectl port-forward svc/gateway 30002:8080
```
**Keep this terminal running!**

**Terminal 2 - Start Streamlit:**
```bash
cd ~/Desktop/microservices-python-app/streamlit-app
python3 -m streamlit run app.py
```

**Or use the convenience script (handles both):**
```bash
cd streamlit-app
./RUN_THIS_FIRST.sh
```

---

### Step 12: Access the Application

1. **Open browser:** http://localhost:8501

2. **Login with default credentials:**
   - Email: `admin@test.com`
   - Password: `admin123`

3. **Upload a video:**
   - Select video file (MP4, AVI, MOV, MKV)
   - Click "Convert to MP3"
   - Wait 10-30 seconds for conversion

4. **Download MP3:**
   - Copy the MP3 file ID shown after conversion
   - Paste it in the "Download MP3" section
   - Click "Fetch MP3" then download

---

## 🎮 Usage Guide

### Upload and Convert
1. Login to the application
2. Upload your video file
3. Click "🎵 Convert to MP3"
4. The system automatically:
   - Stores video in MongoDB
   - Queues conversion job in RabbitMQ
   - Converter service processes the video
   - Extracts audio and saves as MP3
   - Returns MP3 file ID

### Download MP3
1. Copy the MP3 file ID from the upload success message
2. Paste it in the "Download MP3" section
3. Click "Fetch MP3"
4. Click the download button to save your MP3

---

## 🔑 Credentials

### Database Credentials
- **MongoDB:**
  - Username: `lynda`
  - Password: `lynda1234`
  
- **PostgreSQL:**
  - Username: `lynda`
  - Password: `cnd2023`
  - Database: `authdb`

- **RabbitMQ:**
  - Username: `guest`
  - Password: `guest`

### Application Login
- **Email:** `admin@test.com`
- **Password:** `admin123`

---

## 🛠️ Useful Commands

### View Pods
```bash
kubectl get pods
```

### View Logs
```bash
# Gateway logs
kubectl logs -l app=gateway --tail=50

# Converter logs
kubectl logs -l app=converter --tail=50

# Auth logs
kubectl logs -l app=auth --tail=50
```

### Restart Deployment
```bash
kubectl rollout restart deployment/gateway
kubectl rollout restart deployment/converter
```

### RabbitMQ Management UI
```bash
kubectl port-forward svc/rabbitmq 15672:15672
# Open: http://localhost:15672
# Login: guest / guest
```

### Access Databases
```bash
# PostgreSQL
kubectl exec -it deployment/postgres -- psql -U lynda -d authdb

# MongoDB
kubectl exec -it mongodb-0 -- mongosh mongodb://lynda:lynda1234@localhost:27017/mp3s?authSource=admin
```

---

## 🐛 Troubleshooting

### Pods Not Starting
```bash
# Check pod status
kubectl get pods

# Describe pod for details
kubectl describe pod <pod-name>

# View pod logs
kubectl logs <pod-name>
```

### Port Forward Issues
```bash
# Kill existing port forwards
pkill -f "port-forward"

# Restart port forward
kubectl port-forward svc/gateway 30002:8080
```

### Streamlit Connection Error
Make sure:
1. Port forward is running in Terminal 1
2. Gateway pods are running: `kubectl get pods | grep gateway`
3. Streamlit is using correct URL: http://localhost:30002

### Clean Restart
```bash
# Delete all resources
kubectl delete all --all

# Redeploy from Step 4
```

### Minikube Issues
```bash
# Stop and restart Minikube
minikube stop
minikube delete
minikube start --driver=docker --memory=4096 --cpus=2

# Then redeploy from Step 2
```

---

## 🔧 Quick Deploy (One Command)

After prerequisites are installed:

```bash
minikube start --driver=docker --memory=4096 --cpus=2 && \
eval $(minikube docker-env) && \
./build-images.sh && \
kubectl apply -f manifests/ && \
sleep 30 && \
./setup-rabbitmq-queues.sh && \
kubectl apply -f src/auth-service/manifest/ && \
kubectl apply -f src/gateway-service/manifest/ && \
kubectl apply -f src/converter-service/manifest/ && \
kubectl get pods
```

**Note:** Still need to run Streamlit separately (Steps 10-11)

---

## 📊 Architecture Details

### Technology Stack
- **Backend:** Python 3.10, Flask
- **Databases:** PostgreSQL 15, MongoDB 6
- **Message Queue:** RabbitMQ
- **Media Processing:** MoviePy, FFmpeg
- **Authentication:** JWT (PyJWT)
- **Container Orchestration:** Kubernetes (Minikube)
- **Frontend:** Streamlit
- **Storage:** GridFS (MongoDB)

### Data Flow
1. User uploads video via Streamlit UI
2. Gateway validates JWT token with Auth service
3. Video stored in MongoDB (GridFS)
4. Message queued in RabbitMQ
5. Converter service picks up job
6. Video converted to MP3 using MoviePy
7. MP3 stored in MongoDB (GridFS)
8. User retrieves MP3 file ID
9. User downloads MP3 via Gateway

### Scalability
- **Converter Service:** 4 replicas for parallel processing
- **Gateway/Auth:** 2 replicas for high availability
- **RabbitMQ:** Load balances across converter replicas
- **GridFS:** Handles files larger than 16MB MongoDB limit

---

## 📚 Additional Documentation

- **[DEPLOY.md](./DEPLOY.md)** - Quick deployment commands
- **[COMPLETE_SETUP_GUIDE.md](./COMPLETE_SETUP_GUIDE.md)** - Detailed setup guide
- **[MICROSERVICES_FLOW.md](./MICROSERVICES_FLOW.md)** - Technical architecture deep-dive
- **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** - Command cheat sheet

---

## 🎓 What You'll Learn

This project demonstrates:
- Microservices architecture patterns
- Kubernetes deployment and orchestration
- Asynchronous processing with message queues
- JWT authentication flows
- GridFS for large file storage
- Docker containerization
- Horizontal scaling strategies
- RESTful API design

---

## 🤝 Contributing

This is a learning project. Feel free to:
- Add new features (WAV, FLAC support, progress tracking)
- Improve error handling
- Add monitoring/observability
- Implement HTTPS/TLS
- Add user management features

---

## 📝 License

This project is open source and available for educational purposes.

---

## 👤 Author

**Lynda & Ndeye Pathe  - 2026**

Built with ❤️ using Python, Kubernetes, and modern microservices patterns.

---

## 🚀 Next Steps

After successful deployment:
1. ✅ Test video upload and conversion
2. ✅ Explore RabbitMQ management UI
3. ✅ Check MongoDB data with GridFS
4. ✅ Monitor pod logs for system behavior
5. ✅ Try scaling deployments: `kubectl scale deployment/converter --replicas=6`

**Enjoy your video-to-MP3 converter!** 🎉
