import re

from kubernetes import client, config
from kubernetes.client.rest import ApiException
from packaging import version

config.load_kube_config()
v1 = client.CoreV1Api()
    
def get_ingress_nginx_pods():
    pods = v1.list_pod_for_all_namespaces(label_selector="app.kubernetes.io/name=ingress-nginx")
    if pods.items:
        print("ℹ️ It looks like you're using the NGinx ingress controller.")
    else:
        print("✅ No NGinx ingress controller pods found.")
    
    return pods

def get_ingress_nginx_service():
    svc_name = "ingress-nginx-controller-admission"
    svc_namespace = "ingress-nginx"

    print(f"\nChecking service '{svc_name}' in namespace '{svc_namespace}'...")
    try:
        svc = v1.read_namespaced_service(name=svc_name, namespace=svc_namespace)
        svc_type = svc.spec.type
        print(f"ℹ️ Found related service '{svc.metadata.name}' of type: {svc_type}")

        if svc_type == "NodePort":
            for port in svc.spec.ports:
                print(f"  → ⚠️ Port {port.port} is exposed on NodePort {port.node_port}")
        elif svc_type == "LoadBalancer":
            ingress = svc.status.load_balancer.ingress
            if ingress:
                for entry in ingress:
                    print(f"  → ⚠️ LoadBalancer Ingress: {entry.ip or entry.hostname}")
            else:
                print("  → LoadBalancer is provisioned, but no external IP/hostname yet.")
        elif svc_type == "ClusterIP":
            print(f"  → ClusterIP: {svc.spec.cluster_ip}")
        else:
            print(f"  → Additional info: {svc.spec}")
        
        return True
    except ApiException as e:
        if e.status == 404:
            print(f"✅  Service '{svc_name}' not found in namespace '{svc_namespace}'.")
        else:
            print(f"✅  Failed to get service info: {e}")
        return False

def get_ingress_nginx_pod_images():
    controller_pods = v1.list_pod_for_all_namespaces(
        label_selector="app.kubernetes.io/name=ingress-nginx,app.kubernetes.io/component=controller"
    )
    images = []
    for pod in controller_pods.items:
        for container in pod.spec.containers:
            images.append(container.image)     
    return images
            
def main():
    print("Checking for ingress-nginx pods...")
    pods = get_ingress_nginx_pods()
    if not pods:
        return

    svc_found = get_ingress_nginx_service()
    if svc_found:
        images = get_ingress_nginx_pod_images()
        if images:
            print("\n📦 Images used by ingress-nginx controller pods:")
            for img in images:
                print(f"  - {img}")

            
            versions = set()
            for img in images:
                match = re.search(r":v?(\d+\.\d+\.\d+)", img)
                if match:
                    versions.add(match.group(1))

            if versions:
                print("\n🔢 Detected ingress-nginx controller versions:")
                for v in sorted(versions, key=version.parse):
                    v_parsed = version.parse(v)
                    vulnerable = (
                        v_parsed < version.parse("1.11.0")
                        or version.parse("1.11.0") <= v_parsed <= version.parse("1.11.4")
                        or v_parsed == version.parse("1.12.0")
                    )
                    vuln_marker = "🛑 LIKELY VULNERABLE" if vulnerable else "✅ Likely safe"
                    print(f"  → {v}   {vuln_marker}")
            else:
                print("\n⚠️ No version tags found in image names.")
        else:
            print("\n⚠️ No controller pods found to extract images.")


if __name__ == "__main__":
    main()
