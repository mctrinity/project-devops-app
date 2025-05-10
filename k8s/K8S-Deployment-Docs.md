# Kubernetes Deployment Docs for FastAPI To-Do App

This documentation captures the Kubernetes resources and best practices used to deploy a FastAPI-based To-Do API in a secure and scalable way.

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
  template:
    metadata:
      labels:
        app: fastapi-todo
    spec:
      containers:
        - name: fastapi-todo
          image: fastapi-todo:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /docs
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /docs
              port: 8000
            initialDelaySeconds: 15
            periodSeconds: 20
          envFrom:
            - configMapRef:
                name: fastapi-config
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
  type: NodePort
```

---

## ⚙️ ConfigMap: `configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: fastapi-config
  namespace: default
data:
  DB_URL: "sqlite:///./todos.db"
```

---

## 🔐 Secrets: `secrets.yaml`

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
```

> 💡 To encode a secret:
>
> ```bash
> echo -n "your-value" | base64
> ```
>
> 💡 To decode a base64-encoded secret manually:
>
> ```bash
> echo "<base64-string>" | base64 --decode
> ```
>
> 💡 Example:
>
> ```bash
> echo "amF3c2VjcmV0MTIz" | base64 --decode   # Output: jawssecret123
> echo "YXBpa2V5LTIzNDU2Nzg5MA==" | base64 --decode   # Output: apikey-234567890
> ```

> 🔐 **Note on Base64 Encoding:**
> Kubernetes uses base64 to store secrets as a form of basic obfuscation. It helps prevent casual exposure of sensitive values in YAML files and version control. However, base64 is not encryption — anyone with access can decode it using `base64 --decode`. For strong security, enforce RBAC policies and consider integrating tools like Vault or cloud-based secret managers.

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

Ingress acts as a **centralized entry point** to your applications running in Kubernetes. Instead of exposing each service with a separate `NodePort` or `LoadBalancer`, Ingress lets you:

* Use **human-friendly URLs** like `http://todo.local`
* Consolidate routing for multiple apps/services under one controller
* Support **TLS termination** and **custom routing rules**
* Apply **auth, rate limiting, and headers** using annotations
* Avoid consuming external IPs for every service (especially in cloud setups)

---

## 🚀 How to Set Up Ingress in Minikube

### 1. Enable Ingress Addon

```bash
minikube addons enable ingress
```

### 2. Apply the Ingress YAML

```bash
kubectl apply -f k8s/ingress.yaml
```

### 3. Start the Ingress Tunnel

```bash
minikube tunnel
```

> This will expose the ingress controller on `127.0.0.1`.

### 4. Add Local DNS Entry

Edit your `hosts` file:

* **On Windows**:  `C:\Windows\System32\drivers\etc\hosts`
* **On macOS/Linux**:  `/etc/hosts`

Add the following line:

```
127.0.0.1  todo.local
```

### 5. Access Your App

Visit:

```
http://todo.local
```

### 6. Access Swagger UI and ReDoc

* Swagger: `http://todo.local/docs`
* ReDoc: `http://todo.local/redoc`

> ✅ No need to rely on `minikube service` or port numbers anymore!

---

## 🚀 Rollout Commands

```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
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
```

---

## 🐘 PostgreSQL Setup & DB Initialization

If you encounter an error like `FATAL:  database "tododb" does not exist`, it means the FastAPI app couldn't find the expected database in PostgreSQL. To resolve:

```bash
# Enter the Postgres pod
kubectl exec -it <postgres-pod-name> -- psql -U devuser

# Then manually create the database
CREATE DATABASE tododb;
```

After creating the database, restart your FastAPI deployment to trigger table creation:

```bash
kubectl rollout restart deployment fastapi-todo
```

> You can verify table creation with:
>
> ```bash
> kubectl exec -it <postgres-pod> -- psql -U devuser -d tododb
> \dt
> SELECT * FROM todos;
> ```

---

## 🧪 API Testing via Swagger UI

Once the FastAPI app is running, you can interactively test your endpoints using the built-in Swagger UI.

### Access the Swagger UI

If you're using NodePort:

```bash
minikube service fastapi-todo-service
```

➡ This will open a URL in your browser (e.g., `http://127.0.0.1:xxxxx`).

Then navigate to:

```
http://<your-node-port-url>/docs
```

If using Ingress:

```
http://todo.local/docs
```

### Test Examples

#### ✅ Get To-Dos

* Click on the **GET /todos** endpoint.
* Click **"Try it out"**.
* Click **"Execute"** to fetch all current to-dos.

#### ➕ Create a To-Do

* Expand **POST /todos**.
* Click **"Try it out"**.
* Use a request body like:

```json
{
  "title": "Deploy to production",
  "done": false
}
```

* Click **"Execute"** to create it.

#### ✏️ Update a To-Do

* Use **PUT /todos/{todo\_id}** with a valid `todo_id` (e.g., 1).

```json
{
  "title": "Deploy to production 🚀",
  "done": true
}
```

#### ❌ Delete a To-Do

* Use **DELETE /todos/{todo\_id}** to remove a specific item.

---

## 📌 Notes

* Do not log secrets in app code.
* Base64 encoding is not encryption — use external secret managers (e.g., HashiCorp Vault or Azure Key Vault) for higher security.
* Avoid hardcoding sensitive values in images or code.
* To inspect base64 values stored in Kubernetes secrets:

  ```bash
  kubectl get secret fastapi-secret -o yaml
  # or extract and decode one line:
  kubectl get secret fastapi-secret -o jsonpath="{.data.JWT_SECRET}" | base64 --decode
  ```
* 🔁 To rotate a secret:

  ```bash
  # Update your secret file or regenerate base64 string
  kubectl apply -f k8s/secrets.yaml
  kubectl rollout restart deployment fastapi-todo
  ```
* 🔒 To restrict access to secrets:

  * Use Kubernetes RBAC to limit `get`, `list`, and `watch` permissions on Secret resources
  * Avoid assigning unnecessary roles to service accounts
  * Consider using read-only access for observability tools
* 📁 To mount a secret as a file:

  ```yaml
  volumeMounts:
    - name: secret-volume
      mountPath: "/etc/secrets"
      readOnly: true
  volumes:
    - name: secret-volume
      secret:
        secretName: fastapi-secret
  ```

  > This will mount each key (e.g., `JWT_SECRET`) as a file under `/etc/secrets/JWT_SECRET`
  > **Note:** Secrets mounted as files are stored in memory (not on disk) and are not persistent across pod restarts. They are designed for secure, temporary access only.
* 📦 To define persistent volumes for databases or files:

  ```yaml
  kind: PersistentVolumeClaim
  apiVersion: v1
  metadata:
    name: todo-data-pvc
  spec:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 1Gi
  ```

  > Use PVCs for persistent application data like databases — not for secrets or tokens.
