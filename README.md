# FastAPI To-Do App — Project Setup & Overview

This project is a scalable, cloud-native To-Do API built with **FastAPI**, containerized with Docker, and deployed to **Azure Kubernetes Service (AKS)**. It now integrates with a **managed Azure PostgreSQL database**, includes secure secret handling, and is accessible via **NGINX Ingress**.

---

## 📘 Project Overview

* **Framework**: FastAPI
* **Deployment Platform**: Azure Kubernetes Service (AKS)
* **Container Registry**: Azure Container Registry (ACR)
* **Database**: Azure Database for PostgreSQL (Flexible Server)
* **Ingress**: NGINX (with optional TLS support)
* **Secrets Handling**: Kubernetes Secrets (Base64 encoded)
* **Live Docs**: Swagger UI at `/docs`, ReDoc at `/redoc`

---

## 🚀 Quick Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/fastapi-todo-k8s.git
cd fastapi-todo-k8s
```

### 2. Build and Push Docker Image to ACR

```bash
docker build -t fastapi-todo:latest .
docker tag fastapi-todo:latest fastapitodoregistry.azurecr.io/fastapi-todo:v1.0.0
docker push fastapitodoregistry.azurecr.io/fastapi-todo:v1.0.0
```

### 3. Provision Azure Resources

```bash
az group create --name fastapi-rg --location eastus
az acr create --resource-group fastapi-rg --name fastapitodoregistry --sku Basic
az aks create --resource-group fastapi-rg --name fastapi-aks --node-count 2 --enable-addons monitoring --generate-ssh-keys
az aks get-credentials --resource-group fastapi-rg --name fastapi-aks
az aks update -n fastapi-aks -g fastapi-rg --attach-acr fastapitodoregistry
```

---

## 🧰 Install Helm (if not already installed)

Follow [Helm installation instructions](https://helm.sh/docs/intro/install/) or:

```bash
choco install kubernetes-helm     # Windows (via Chocolatey)
brew install helm                 # macOS (via Homebrew)
```

---

## 🌐 Deploy NGINX Ingress

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx-ingress ingress-nginx/ingress-nginx --create-namespace --namespace ingress-nginx
```

---

## 📦 Apply Kubernetes Manifests

```bash
kubectl apply -f k8s/fastapi-secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

> Ensure `fastapi-secret.yaml` contains the `DB_URL` that points to your Azure PostgreSQL server.

---

## 🛡️ Azure PostgreSQL Firewall Setup

Make sure to allow access from your AKS cluster to Azure Database:

```bash
az network public-ip list -g MC_fastapi-rg_fastapi-aks_eastus --query "[].ipAddress" -o tsv
```

Go to **Azure Portal > PostgreSQL Flexible Server > Networking > Firewall rules** and add your AKS public IP.

---

## 🐘 Create the Database (if not auto-created)

Start a temporary PostgreSQL client pod:

```yaml
# postgres-client.yaml
apiVersion: v1
kind: Pod
metadata:
  name: psql-client
spec:
  containers:
    - name: psql-client
      image: postgres:15
      command: ['sleep', '3600']
```

```bash
kubectl apply -f k8s/postgres-client.yaml
kubectl exec -it psql-client -- psql "<your-DB-URL>"
CREATE DATABASE tododb;
```

---

## ✅ Verify & Access the Application

### Check Application Status

```bash
kubectl get pods
kubectl get ingress
```

### Test Access via Ingress

Once your ingress controller is ready, use the external IP:

```
http://<EXTERNAL-IP>.nip.io/docs
```

---

## 🔐 Secrets Management

* Store secrets in `fastapi-secret.yaml` using base64-encoded values
* Rotate secrets as needed:

```bash
kubectl apply -f k8s/fastapi-secret.yaml
kubectl rollout restart deployment fastapi-todo
```

---

## 📌 Clean-Up

If you migrated to Azure PostgreSQL, delete these files:

* `postgres-deployment.yaml`
* `postgres-service.yaml`
* `postgres-pvc.yaml`
* `postgres-secret.yaml`
* `stuck-pv.json`, `stuck-pvc.json`

---

## 🎉 Done!

You're now running a FastAPI app in a secure, production-grade Azure Kubernetes environment with managed PostgreSQL support!
