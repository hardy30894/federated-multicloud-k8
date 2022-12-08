# Deploy Federated Multi-Cloud Kubernetes Clusters

This is a repository with part of the configuration to **Deploy
Federated Multi-Cloud Kubernetes Clusters**. It contains Terraform
configuration files to deploy a Consul-federated
multi-cluster Kubernetes setup for Image Classfication.

![assets](https://user-images.githubusercontent.com/70341313/205536186-61fb1553-5dd0-436b-8b0d-950beab436af.png)

### Remove Previous configuration
```
rm -f ~/.kube/config
```

### Provision an EKS Cluster
```
cd eks
terraform init
terraform apply --auto-approve
```

### Provision an AKS Cluster
```
cd ../aks
terraform init
terraform apply --auto-approve
```

### Configure kubectl
```
cd ../eks
aws eks --region $(terraform output -raw region) update-kubeconfig --name $(terraform output -raw cluster_name) --alias eks
```

```
cd ../aks
az aks get-credentials --resource-group $(terraform output -raw resource_group_name) --name $(terraform output -raw kubernetes_cluster_name) --context aks
```

### Verify ProxyDefaults configuration is commented
```
cd ../consul
vi proxy_defaults.tf
```

### Deploy Consul and configure cluster federation
```
terraform init
terraform apply --auto-approve
```

### Deploy ProxyDefaults
```
vi proxy_defaults.tf
# Uncomment the ProxyDefaults configuration
terraform apply --auto-approve
```


### Verify cluster federation
```
kubectl get pods --context eks
kubectl get proxydefaults --context eks
kubectl get pods --context aks
kubectl get proxydefaults --context aks
kubectl exec statefulset/consul-server --context aks -- consul members -wan
```

### Deploy an application
```
cd ../counting-service
terraform init
terraform apply --auto-approve
```

### Run the application
```
kubectl port-forward dashboard 9002:9002 --context eks
```

### Verify aplication is running
```
http://localhost:9002/ 
```


