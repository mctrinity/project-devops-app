# FastAPI To-Do App — Project Setup & Overview

This project is a simple, scalable To-Do application built with **FastAPI** and deployed using **Kubernetes**. It includes environment configuration via ConfigMaps and Secrets, as well as PostgreSQL integration with persistent storage.

---

## 📘 Project Overview

* **Framework**: FastAPI
* **Containerized**: Docker
* **Deployment**: Kubernetes (Minikube or compatible cluster)
* **Database**: PostgreSQL (deployed as a Pod with PersistentVolumeClaim)
* **Secrets Handling**: Kubernetes Secrets (Base64 encoded)
* **Live API Docs**: Swagger UI at `/docs`

---

## 🚀 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-org/fastapi-todo-k8s.git
cd fastapi-todo-k8s
```

### 2. Build Docker Image

Ensure Docker is running:

```bash
docker build -t fastapi-todo:latest .
```

### 3. Set Up Minikube (or your K8s cluster)

```bash
minikube start
minikube kubectl -- get pods
```

(Optional) Enable Minikube Docker env:

```bash
minikube -p minikube docker-env --shell powershell | Invoke-Expression
```

### 4. Apply Kubernetes Resources

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 5. Initialize Database (if needed)

```bash
kubectl exec -it <postgres-pod-name> -- psql -U devuser
CREATE DATABASE tododb;
```

Then restart the app deployment:

```bash
kubectl rollout restart deployment fastapi-todo
```

---

## 🧪 Testing the API

```bash
minikube service fastapi-todo-service
```

* Access Swagger UI via `/docs` endpoint.
* Try out **GET /todos**, **POST /todos**, **PUT /todos/{id}**, and **DELETE /todos/{id}**.

---

## 🛠️ Notes

* To verify environment variables:

  ```bash
  kubectl exec -it <pod-name> -- env | grep DB_URL
  ```
* To inspect DB:

  ```bash
  kubectl exec -it <postgres-pod> -- psql -U devuser -d tododb
  \dt
  SELECT * FROM todos;
  ```

---

## 🔐 Managing Secrets

* Use `base64` to encode values for `secrets.yaml`
* Rotate secrets by reapplying the YAML and restarting the deployment:

  ```bash
  kubectl apply -f k8s/secrets.yaml
  kubectl rollout restart deployment fastapi-todo
  ```

---

## ✅ Done!

Your FastAPI app should now be deployed and connected to a persistent PostgreSQL instance — all managed via Kubernetes. Happy coding!
