# IngressNightmare (CVE-2025-1974)

This Python script can help you understand if you're running the Ingress NGINX Controller, and if yes if it's using a known vulnerable version.

## Usage

First, make sure to install `uv` [from here](https://docs.astral.sh/uv/#installation) and then run the script against the Kubernetes cluster to audit.

```
uv run --with kubernetes,packaging check.py
```

## Sample outputs

### Vulnerable cluster:

```
Checking for ingress-nginx pods...
ℹ️ It looks like you're using the NGinx ingress controller.

Checking service 'ingress-nginx-controller-admission' in namespace 'ingress-nginx'...
ℹ️ Found related service 'ingress-nginx-controller-admission' of type: ClusterIP
  → ClusterIP: 10.100.127.164

📦 Images used by ingress-nginx controller pods:
  - registry.k8s.io/ingress-nginx/controller:v1.12.0@sha256:e6b8de175acda6ca913891f0f727bca4527e797d52688cbe9fec9040d6f6b6fa

🔢 Detected ingress-nginx controller versions:
  → 1.12.0   🛑 LIKELY VULNERABLE
```

### Cluster running a non-vulnerable version:

```
Checking for ingress-nginx pods...
ℹ️ It looks like you're using the NGinx ingress controller.

Checking service 'ingress-nginx-controller-admission' in namespace 'ingress-nginx'...
ℹ️ Found related service 'ingress-nginx-controller-admission' of type: ClusterIP
  → ClusterIP: 10.96.74.187

📦 Images used by ingress-nginx controller pods:
  - registry.k8s.io/ingress-nginx/controller:v1.12.1@sha256:d2fbc4ec70d8aa2050dd91a91506e998765e86c96f32cffb56c503c9c34eed5b

🔢 Detected ingress-nginx controller versions:
  → 1.12.1   ✅ Likely safe
```

## Credit
- https://github.com/DataDog/security-labs-pocs/tree/main/validation-scripts/cve-2025-1974-ingress-nightmare
