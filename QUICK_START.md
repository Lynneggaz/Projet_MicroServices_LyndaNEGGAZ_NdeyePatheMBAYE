# Deployment Commands - Video to MP3 Converter

## Prerequisites
```bash
# Verify installations
minikube version
docker --version
kubectl version --client
python3 --version
```

---

## Step 1: Start Minikube
```bash
minikube start --driver=docker --memory=4096 --cpus=2
minikube status
```

---

## Step 2: Configure Docker Environment
```bash
eval $(minikube docker-env)
```

---

## Step 3: Build Docker Images
```bash
cd ~/Desktop/microservices-python-app
./build-images.sh
```

**Wait for build to complete (~5-10 minutes)**

---

## Step 4: Deploy Databases
```bash
# PostgreSQL
kubectl apply -f manifests/postgres.yaml

# MongoDB
kubectl apply -f manifests/mongodb.yaml

# RabbitMQ
kubectl apply -f manifests/rabbitmq.yaml

# Wait for databases to be ready
kubectl get pods -w
```

**Press Ctrl+C when all 3 database pods show "Running" and "1/1"**

---

## Step 5: Setup RabbitMQ Queues
```bash
./setup-rabbitmq-queues.sh
```

---

## Step 6: Deploy Auth Service
```bash
kubectl apply -f src/auth-service/manifest/configmap.yaml
kubectl apply -f src/auth-service/manifest/secret.yaml
kubectl apply -f src/auth-service/manifest/service.yaml
kubectl apply -f src/auth-service/manifest/deployment.yaml
```

---

## Step 7: Deploy Gateway Service
```bash
kubectl apply -f src/gateway-service/manifest/configmap.yaml
kubectl apply -f src/gateway-service/manifest/secret.yaml
kubectl apply -f src/gateway-service/manifest/service.yaml
kubectl apply -f src/gateway-service/manifest/gateway-deploy.yaml
```

---

## Step 8: Deploy Converter Service
```bash
kubectl apply -f src/converter-service/manifest/configmap.yaml
kubectl apply -f src/converter-service/manifest/secret.yaml
kubectl apply -f src/converter-service/manifest/converter-deploy.yaml
```

---

## Step 9: Deploy Notification Service
```bash
kubectl apply -f src/notification-service/manifest/configmap.yaml
kubectl apply -f src/notification-service/manifest/secret.yaml
kubectl apply -f src/notification-service/manifest/notification-deploy.yaml
```

---

## Step 10: Verify All Pods Running
```bash
kubectl get pods
```

**Expected: 13 pods all showing "Running" status**

---

## Step 11: Install Streamlit Dependencies
```bash
cd streamlit-app
pip3 install -r requirements.txt
```

---

## Step 12: Run Application

**Terminal 1 - Port Forward:**
```bash
kubectl port-forward svc/gateway 30002:8080
```

**Terminal 2 - Streamlit:**
```bash
cd streamlit-app
python3 -m streamlit run app.py
```

**Or use the convenience script:**
```bash
cd streamlit-app
./RUN_THIS_FIRST.sh
```

---

## Step 13: Access Application
```
Open browser: http://localhost:8501

Login credentials:
  Email: admin@test.com
  Password: admin123
```

---

## Quick Verification Commands

```bash
# Check all pods
kubectl get pods

# Check services
kubectl get svc

# View logs
kubectl logs -l app=gateway --tail=20
kubectl logs -l app=converter --tail=20

# RabbitMQ UI (optional)
kubectl port-forward svc/rabbitmq 15672:15672
# Open: http://localhost:15672 (guest/guest)
```

---

## Troubleshooting

**Pods not ready?**
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

**Clean restart:**
```bash
kubectl delete all --all
# Then start from Step 4
```

**Minikube issues:**
```bash
minikube stop
minikube delete
minikube start --driver=docker --memory=4096 --cpus=2
```

---

## One-Command Deploy (After Prerequisites)

```bash
# All in one (from project root)
minikube start --driver=docker --memory=4096 --cpus=2 && \
eval $(minikube docker-env) && \
./build-images.sh && \
kubectl apply -f manifests/postgres.yaml -f manifests/mongodb.yaml -f manifests/rabbitmq.yaml && \
sleep 30 && \
./setup-rabbitmq-queues.sh && \
kubectl apply -f src/auth-service/manifest/ && \
kubectl apply -f src/gateway-service/manifest/ && \
kubectl apply -f src/converter-service/manifest/ && \
kubectl apply -f src/notification-service/manifest/ && \
kubectl get pods
```

**Note:** Wait for all pods to be running before accessing the app

---

**By: Lynda - 2026**
