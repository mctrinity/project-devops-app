# Kubernetes Deployment Docs for FastAPI To-Do App (External PostgreSQL Edition)

This documentation captures the Kubernetes resources and best practices used to deploy a FastAPI-based To-Do API in a secure and scalable way, now using **Azure Database for PostgreSQL** instead of an in-cluster database.

---

## 📦 Deployment: `deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fastapi-todo
  labels:
    app: fastapi-todo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fastapi-todo
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: fastapi-todo
    spec:
      containers:
        - name: fastapi-todo
          image: fastapitodoregistry.azurecr.io/fastapi-todo:v1.0.0
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          securityContext:
            runAsNonRoot: true
            runAsUser: 1000
            allowPrivilegeEscalation: false
          envFrom:
            - secretRef:
                name: fastapi-secret
```

---

## 🌐 Service: `service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: fastapi-todo-service
spec:
  selector:
    app: fastapi-todo
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: ClusterIP  # Ingress will route traffic to this service
```

> 💡 You only need `type: NodePort` if you want direct external access without Ingress. For Ingress setups (recommended), `ClusterIP` is sufficient and preferred.

---

## 🔐 Secrets: `fastapi-secret.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: fastapi-secret
  namespace: default
type: Opaque
data:
  JWT_SECRET: amF3c2VjcmV0MTIz           # "jawssecret123"
  API_KEY: YXBpa2V5LTIzNDU2Nzg5MA==      # "apikey-234567890"
  DB_URL: <base64-encoded-external-postgres-url>
```

> 💡 To encode your DB URL:
>
> ```bash
> echo -n "postgresql://devuser:YourPassword@your-db-name.postgres.database.azure.com:5432/tododb" | base64
> ```

---

## 🌐 Ingress: `ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: fastapi-todo-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
    - host: todo.local
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: fastapi-todo-service
                port:
                  number: 80
```

---

## 🧭 Why Use Ingress?

Ingress provides a centralized entry point to your application:

* Friendly URLs (e.g., `http://todo.local`)
* No need for multiple LoadBalancers or NodePorts
* Supports TLS termination, authentication, path-based routing

---

## 🚀 How to Set Up Ingress in Minikube

### 1. Enable Ingress Addon

```bash
minikube addons enable ingress
```

### 2. Apply Ingress YAML

```bash
kubectl apply -f k8s/ingress.yaml
```

### 3. Start the Ingress Tunnel

```bash
minikube tunnel
```

### 4. Add Hosts Entry

```txt
127.0.0.1  todo.local
```

### 5. Access App:

* Swagger: `http://todo.local/docs`
* ReDoc: `http://todo.local/redoc`

---

## 🚀 Rollout Commands

```bash
kubectl apply -f k8s/fastapi-secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
kubectl rollout restart deployment fastapi-todo
```

---

## ✅ Environment Verification

```bash
kubectl exec -it <pod-name> -- env | grep JWT_SECRET
kubectl exec -it <pod-name> -- env | grep API_KEY
kubectl exec -it <pod-name> -- env | grep DB_URL
```

---

## 🐘 PostgreSQL Setup in Azure

You no longer need in-cluster Postgres. Instead:

1. Create a flexible server:

```bash
az postgres flexible-server create \
  --resource-group fastapi-rg \
  --name fastapi-prod-db \
  --location eastus \
  --admin-user devuser \
  --admin-password YourSecurePassword123! \
  --tier Burstable \
  --sku-name Standard_B1ms \
  --version 15 \
  --storage-size 32
```

2. Allow traffic:

```bash
az postgres flexible-server firewall-rule create \
  --resource-group fastapi-rg \
  --name fastapi-prod-db \
  --rule-name allow-all \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 255.255.255.255
```

3. Connect via FastAPI using the DB URL in your secret.

---

## 🧪 API Testing via Swagger UI

Once the FastAPI app is running:

```
http://todo.local/docs
```

Try:

* `GET /todos`
* `POST /todos`
* `PUT /todos/{todo_id}`
* `DELETE /todos/{todo_id}`

---

## 🧼 Cleanup Notes

* You no longer need:

  * `postgres-deployment.yaml`
  * `postgres-secret.yaml`
  * `postgres-service.yaml`
  * `postgres-pvc.yaml`
  * `configmap.yaml`

* Ensure `.gitignore` includes:

  ```gitignore
  k8s/*secret*.yaml
  k8s/*copy*.yaml
  ```

---

You're now running a clean, cloud-native FastAPI app with secure external PostgreSQL integration via Azure! 🚀
