# 📦 Helm Guide: Kubernetes Package Manager

Helm is the de facto package manager for Kubernetes. It helps you define, install, and manage Kubernetes applications using pre-configured templates called **charts**.

---

## 🎯 Why Use Helm?

* **Simplify deployments**: Deploy complex applications with one command.
* **Reusable templates**: Charts allow parameterized Kubernetes manifests.
* **Versioning and upgrades**: Track releases and roll back to previous versions easily.
* **Community charts**: Access thousands of open-source charts from Artifact Hub.

---

## ⚙️ Installing Helm (PowerShell)

```powershell
winget install Helm.Helm
```

Or download from [https://helm.sh](https://helm.sh) and add it to your system path.

Verify installation:

```powershell
helm version
```

---

## 🚀 Helm Commands Cheatsheet

| Action                | Command                              |
| --------------------- | ------------------------------------ |
| Add repo              | `helm repo add <name> <url>`         |
| Update repos          | `helm repo update`                   |
| Search charts         | `helm search repo <name>`            |
| Install a chart       | `helm install <release> <chart>`     |
| Upgrade a release     | `helm upgrade <release> <chart>`     |
| Uninstall a release   | `helm uninstall <release>`           |
| List installed charts | `helm list`                          |
| Show chart details    | `helm show chart <chart>`            |
| Rollback a release    | `helm rollback <release> <revision>` |

---

## 📁 Structure of a Helm Chart

```text
mychart/
├── Chart.yaml          # Metadata about the chart
├── values.yaml         # Default configuration values
├── charts/             # Subcharts (dependencies)
├── templates/          # Kubernetes manifest templates
│   └── deployment.yaml
│   └── service.yaml
└── .helmignore         # Files to ignore when packaging
```

---

## 🌍 Example: Installing NGINX Ingress

```powershell
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install nginx-ingress ingress-nginx/ingress-nginx
```

---

## 🔧 Customizing Charts with `values.yaml`

Override default values:

```powershell
helm install my-app ./mychart -f custom-values.yaml
```

Or set inline:

```powershell
helm install my-app ./mychart --set image.tag=v1.2.3
```

---

## 📦 Packaging & Sharing Your Chart

```powershell
helm package mychart/
helm push mychart-0.1.0.tgz oci://your.registry.io/charts
```

---

## 🔍 Resources

* Official Site: [https://helm.sh](https://helm.sh)
* Artifact Hub: [https://artifacthub.io](https://artifacthub.io)
* Helm Docs: [https://helm.sh/docs](https://helm.sh/docs)

---

Helm streamlines Kubernetes application delivery and maintenance. Once familiar, it becomes an essential part of your DevOps toolkit.
