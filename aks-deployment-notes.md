# AKS Deployment Guide for FastAPI App

This guide documents the step-by-step deployment of a FastAPI application to Azure Kubernetes Service (AKS), including the container registry setup, deployment commands, the PostgreSQL client pod for database initialization, and the key issues encountered along the way.

---

## ☁️ Azure Setup

### 1. Create a Resource Group

```bash
az group create --name fastapi-rg --location eastus
```

### 2. Create an AKS Cluster

```bash
az aks create \
  --resource-group fastapi-rg \
  --name fastapi-aks \
  --node-count 2 \
  --enable-addons monitoring \
  --generate-ssh-keys
```

### 3. Get AKS Credentials for kubectl

```bash
az aks get-credentials --resource-group fastapi-rg --name fastapi-aks
```

### 4. Verify Nodes

```bash
kubectl get nodes
```

---

## 🐳 Container Registry & Image Push

### 5. Create Azure Container Registry (ACR)

```bash
az acr create --resource-group fastapi-rg --name fastapitodoregistry --sku Basic
```

### 6. Login to ACR

```bash
az acr login --name fastapitodoregistry
```

### 7. Tag Local Docker Image for ACR

```bash
docker tag fastapi-todo:latest fastapitodoregistry.azurecr.io/fastapi-todo:v1.0.0
```

### 8. Push Image to ACR

```bash
docker push fastapitodoregistry.azurecr.io/fastapi-todo:v1.0.0
```

### 9. Allow AKS to Pull from ACR

```bash
az aks update -n fastapi-aks -g fastapi-rg --attach-acr fastapitodoregistry
```

> This is required once. Without it, AKS pods will fail with `ImagePullBackOff` or `ErrImageNeverPull`.

---

## 📦 Install Helm (for Ingress setup)

### On Windows via Chocolatey

```bash
choco install kubernetes-helm
```

### On macOS via Homebrew

```bash
brew install helm
```

### On Linux

```bash
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Verify installation:

```bash
helm version
```

---

## 🚀 Deploy Kubernetes Resources

### 10. Apply All Manifests

```bash
kubectl apply -f k8s/
```

### 11. Verify Everything is Running

```bash
kubectl get pods
kubectl get services
kubectl get ingress
```

---

## 🔐 Configure Azure PostgreSQL Firewall

Go to your Azure PostgreSQL Flexible Server > Networking:

* Set **Public access** to "Selected networks"
* Add inbound rule for the **AKS outbound public IPs** (found via:

  ```bash
  az network public-ip list -g MC_<resource-group>_<aks-name>_<region> --query "[].ipAddress" -o tsv
  ```

)

---

## 🐘 Initialize PostgreSQL via psql-client Pod

### postgres-client.yaml

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: psql-client
spec:
  containers:
    - name: psql-client
      image: postgres:15
      command: ['sleep', 'infinity']
```

```bash
kubectl apply -f k8s/postgres-client.yaml
kubectl exec -it psql-client -- psql "<DB_URL_FROM_SECRET>"
```

Inside psql:

```sql
CREATE DATABASE tododb;
\c tododb;
CREATE TABLE todos (id SERIAL PRIMARY KEY, title TEXT, done BOOLEAN);
```

---

## ⚠️ Troubleshooting Notes

### ❌ ImagePullBackOff / ErrImageNeverPull

```text
fastapi-todo-xxx   0/1   ImagePullBackOff / ErrImageNeverPull
```

**Fix:**

* Ensure the image is pushed to ACR
* Ensure `imagePullPolicy: Always` in the deployment
* Run `az aks update --attach-acr` to authorize AKS access to ACR

### ❌ PostgreSQL Connection Timeout / Refused

Ensure:

* DB name exists
* AKS public IP is whitelisted in PostgreSQL firewall
* Connection string is correct and secret is updated properly

---

## ✅ Final Deployment Flow Recap

1. Build and tag Docker image
2. Push image to ACR
3. Authorize AKS to pull from ACR
4. Apply manifests (FastAPI, Ingress, etc.)
5. Patch firewall and DB init via psql-client
6. Verify via `kubectl get pods`
7. Access the app via Ingress

You're now running a cloud-native FastAPI app on AKS! 🚀
