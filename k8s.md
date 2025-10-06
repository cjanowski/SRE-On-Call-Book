# Kubernetes SRE Runbook

## Table of Contents
1. [Emergency Contacts](#emergency-contacts)
2. [Cluster Health Checks](#cluster-health-checks)
3. [Common Issues and Resolutions](#common-issues-and-resolutions)
4. [Node Management](#node-management)
5. [Pod Troubleshooting](#pod-troubleshooting)
6. [Network Issues](#network-issues)
7. [Storage Issues](#storage-issues)
8. [Performance Troubleshooting](#performance-troubleshooting)
9. [Security Incidents](#security-incidents)
10. [Backup and Recovery](#backup-and-recovery)

---

## Emergency Contacts

| Role | Contact | Escalation Path |
|------|---------|----------------|
| On-Call Engineer | [Contact Info] | Primary |
| Team Lead | [Contact Info] | Secondary |
| Platform Team | [Contact Info] | Tertiary |
| Cloud Provider Support | [Support Number] | Emergency |

---

## Cluster Health Checks

### Quick Health Assessment

```bash
# Check cluster nodes
kubectl get nodes

# Check system pods
kubectl get pods -n kube-system

# Check all namespaces for issues
kubectl get pods --all-namespaces | grep -v Running

# Check cluster component status
kubectl get componentstatuses
```

### Detailed Health Metrics

```bash
# Check node resource usage
kubectl top nodes

# Check pod resource usage
kubectl top pods --all-namespaces

# View cluster events
kubectl get events --all-namespaces --sort-by='.lastTimestamp'

# Check API server health
kubectl get --raw /healthz
```

---

## Common Issues and Resolutions

### Issue: Pods Stuck in Pending State

**Symptoms:**
- Pods remain in Pending state
- Applications fail to start

**Diagnosis:**
```bash
# Check pod details
kubectl describe pod <pod-name> -n <namespace>

# Check for resource constraints
kubectl describe nodes | grep -A 5 "Allocated resources"

# Check for PVC issues
kubectl get pvc -n <namespace>
```

**Resolution:**
1. Check if there are sufficient resources (CPU/Memory) on nodes
2. Verify PersistentVolumeClaims are bound
3. Check for node taints and pod tolerations
4. Verify node affinity rules
5. Scale cluster if resources are exhausted

```bash
# If resource constrained, scale nodes (example for managed clusters)
# AWS EKS
eksctl scale nodegroup --cluster=<cluster-name> --name=<nodegroup-name> --nodes=<desired-count>

# GKE
gcloud container clusters resize <cluster-name> --num-nodes=<count>
```

---

### Issue: CrashLoopBackOff

**Symptoms:**
- Pod repeatedly crashes and restarts
- Application unavailable

**Diagnosis:**
```bash
# Check pod status
kubectl get pod <pod-name> -n <namespace>

# View pod logs
kubectl logs <pod-name> -n <namespace> --previous

# Describe pod for events
kubectl describe pod <pod-name> -n <namespace>

# Check if liveness/readiness probes failing
kubectl get pod <pod-name> -n <namespace> -o yaml | grep -A 10 "livenessProbe\|readinessProbe"
```

**Resolution:**
1. Review application logs for errors
2. Check probe configurations (timeout, threshold)
3. Verify environment variables and ConfigMaps
4. Check resource limits (OOMKilled)
5. Verify secrets are correctly mounted
6. Roll back to previous working version if needed

```bash
# Rollback deployment
kubectl rollout undo deployment/<deployment-name> -n <namespace>

# Check rollout status
kubectl rollout status deployment/<deployment-name> -n <namespace>
```

---

### Issue: ImagePullBackOff

**Symptoms:**
- Pods cannot pull container images
- New deployments fail

**Diagnosis:**
```bash
# Check pod events
kubectl describe pod <pod-name> -n <namespace>

# Verify image name and tag
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].image}'

# Check image pull secrets
kubectl get secrets -n <namespace>
```

**Resolution:**
1. Verify image exists in registry
2. Check image pull secrets are correctly configured
3. Verify registry credentials are valid
4. Check network connectivity to registry
5. Verify node has sufficient disk space

```bash
# Create image pull secret if missing
kubectl create secret docker-registry <secret-name> \
  --docker-server=<registry-url> \
  --docker-username=<username> \
  --docker-password=<password> \
  --docker-email=<email> \
  -n <namespace>

# Update deployment to use secret
kubectl patch serviceaccount default -n <namespace> \
  -p '{"imagePullSecrets": [{"name": "<secret-name>"}]}'
```

---

## Node Management

### Node is NotReady

**Diagnosis:**
```bash
# Check node status
kubectl get nodes

# Describe problematic node
kubectl describe node <node-name>

# Check node conditions
kubectl get node <node-name> -o jsonpath='{.status.conditions[?(@.status=="True")]}'

# SSH to node and check kubelet
# systemctl status kubelet
# journalctl -u kubelet -n 100
```

**Resolution:**
1. Check kubelet service status on the node
2. Verify network connectivity
3. Check disk pressure or memory pressure
4. Restart kubelet if necessary
5. Cordon and drain node if issues persist, then replace

```bash
# Cordon node (prevent new pods)
kubectl cordon <node-name>

# Drain node (evict pods gracefully)
kubectl drain <node-name> --ignore-daemonsets --delete-emptydir-data

# After fixing, uncordon
kubectl uncordon <node-name>
```

### High Node Resource Usage

**Diagnosis:**
```bash
# Check top resource consumers
kubectl top pods --all-namespaces | sort -k 3 -rn | head -20

# Check node allocatable vs requested
kubectl describe node <node-name> | grep -A 5 "Allocated resources"
```

**Resolution:**
1. Identify pods consuming excessive resources
2. Check if pods have appropriate resource limits
3. Scale down non-critical workloads if needed
4. Add nodes to cluster
5. Optimize application resource usage

---

## Pod Troubleshooting

### Debugging Running Pods

```bash
# Execute commands in pod
kubectl exec -it <pod-name> -n <namespace> -- /bin/sh

# For multi-container pods
kubectl exec -it <pod-name> -n <namespace> -c <container-name> -- /bin/sh

# View logs (follow mode)
kubectl logs -f <pod-name> -n <namespace>

# View logs for previous container instance
kubectl logs <pod-name> -n <namespace> --previous

# Copy files from pod
kubectl cp <namespace>/<pod-name>:/path/to/file ./local-file

# Port forward for debugging
kubectl port-forward <pod-name> -n <namespace> 8080:80
```

### Debugging Pods with Ephemeral Containers

```bash
# Add ephemeral debug container (Kubernetes 1.23+)
kubectl debug <pod-name> -n <namespace> -it --image=busybox --target=<container-name>

# Create debug pod that copies target pod
kubectl debug <pod-name> -n <namespace> --copy-to=<debug-pod-name> --container=<container-name>
```

---

## Network Issues

### Pod-to-Pod Communication Failures

**Diagnosis:**
```bash
# Check network policies
kubectl get networkpolicies -n <namespace>

# Describe network policy
kubectl describe networkpolicy <policy-name> -n <namespace>

# Check pod IPs
kubectl get pods -n <namespace> -o wide

# Test connectivity from pod
kubectl exec -it <source-pod> -n <namespace> -- ping <destination-pod-ip>
kubectl exec -it <source-pod> -n <namespace> -- curl <service-name>.<namespace>.svc.cluster.local
```

**Resolution:**
1. Verify network policies allow traffic
2. Check CNI plugin health
3. Verify DNS resolution is working
4. Check firewall rules (cloud provider level)
5. Validate service endpoints

```bash
# Check service endpoints
kubectl get endpoints <service-name> -n <namespace>

# Check DNS resolution
kubectl run -it --rm debug --image=busybox --restart=Never -- nslookup <service-name>.<namespace>.svc.cluster.local
```

### Service Not Accessible

**Diagnosis:**
```bash
# Check service configuration
kubectl get svc <service-name> -n <namespace> -o yaml

# Check endpoints
kubectl get endpoints <service-name> -n <namespace>

# Check pod labels match service selector
kubectl get pods -n <namespace> --show-labels
```

**Resolution:**
1. Verify service selector matches pod labels
2. Check target port matches container port
3. Verify pods are running and ready
4. Check network policies
5. For LoadBalancer services, check cloud provider configuration

---

## Storage Issues

### PersistentVolumeClaim Stuck in Pending

**Diagnosis:**
```bash
# Check PVC status
kubectl get pvc -n <namespace>

# Describe PVC
kubectl describe pvc <pvc-name> -n <namespace>

# Check available PVs
kubectl get pv

# Check storage classes
kubectl get storageclass
```

**Resolution:**
1. Verify StorageClass exists and is properly configured
2. Check if dynamic provisioning is enabled
3. Verify sufficient storage quota in cloud provider
4. Check PV access modes match PVC requirements
5. Manually create PV if using static provisioning

```bash
# Check storage class details
kubectl describe storageclass <storage-class-name>

# Check PV reclaim policy
kubectl get pv -o custom-columns=NAME:.metadata.name,RECLAIM:.spec.persistentVolumeReclaimPolicy
```

### Disk Pressure on Nodes

**Diagnosis:**
```bash
# Check node conditions
kubectl describe node <node-name> | grep DiskPressure

# Check disk usage on node (requires SSH access)
# df -h
# du -sh /var/lib/kubelet/*
# du -sh /var/lib/docker/*
```

**Resolution:**
1. Clean up unused images and containers
2. Remove old logs
3. Increase disk size
4. Implement log rotation
5. Set up monitoring and alerts

```bash
# Clean up on node (if accessible)
# docker system prune -a -f
# crictl rmi --prune

# Via kubectl
kubectl get pods --all-namespaces -o wide | grep <node-name>
# Consider evicting non-critical pods
```

---

## Performance Troubleshooting

### High CPU Usage

**Diagnosis:**
```bash
# Identify high CPU pods
kubectl top pods --all-namespaces | sort -k 3 -rn | head -20

# Check pod resource limits
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].resources}'

# Profile application (if supported)
kubectl exec -it <pod-name> -n <namespace> -- <profiling-command>
```

**Resolution:**
1. Scale application horizontally if CPU-bound
2. Adjust resource limits and requests
3. Optimize application code
4. Implement HorizontalPodAutoscaler
5. Consider vertical pod autoscaling

```bash
# Create HPA
kubectl autoscale deployment <deployment-name> -n <namespace> \
  --cpu-percent=70 --min=2 --max=10

# Check HPA status
kubectl get hpa -n <namespace>
```

### High Memory Usage

**Diagnosis:**
```bash
# Identify high memory pods
kubectl top pods --all-namespaces | sort -k 4 -rn | head -20

# Check for OOMKilled pods
kubectl get pods --all-namespaces | grep OOMKilled

# Check memory limits
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].resources.limits.memory}'
```

**Resolution:**
1. Check for memory leaks in application
2. Increase memory limits if legitimate usage
3. Implement proper garbage collection
4. Use memory profiling tools
5. Consider using Vertical Pod Autoscaler

---

## Security Incidents

### Unauthorized Access Detected

**Immediate Actions:**
1. Isolate affected pods/nodes
2. Review audit logs
3. Check for privilege escalation
4. Rotate credentials and secrets
5. Review RBAC policies

```bash
# Check who has access
kubectl auth can-i --list --as=<user>

# Review RBAC
kubectl get rolebindings,clusterrolebindings --all-namespaces -o wide

# Check pod security policies
kubectl get psp

# Review audit logs (location varies by setup)
# Example for managed clusters - check cloud provider logging
```

### Suspicious Pod Activity

**Diagnosis:**
```bash
# Check pod security context
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.securityContext}'

# Check container security context
kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[*].securityContext}'

# Review pod events
kubectl get events -n <namespace> --field-selector involvedObject.name=<pod-name>
```

**Actions:**
1. Delete suspicious pods immediately
2. Review deployment manifests
3. Check image sources
4. Review network traffic
5. Scan for vulnerabilities

```bash
# Delete pod
kubectl delete pod <pod-name> -n <namespace> --force --grace-period=0

# Check image for vulnerabilities (using trivy as example)
# trivy image <image-name>
```

---

## Backup and Recovery

### Backup Critical Resources

```bash
# Backup all resources in namespace
kubectl get all -n <namespace> -o yaml > backup-<namespace>-$(date +%Y%m%d).yaml

# Backup specific resource types
kubectl get deployment,service,configmap,secret -n <namespace> -o yaml > backup-resources.yaml

# Backup RBAC
kubectl get clusterroles,clusterrolebindings,roles,rolebindings --all-namespaces -o yaml > backup-rbac.yaml

# Backup persistent volumes
kubectl get pv,pvc --all-namespaces -o yaml > backup-storage.yaml
```

### Restore from Backup

```bash
# Restore resources
kubectl apply -f backup-<namespace>-<date>.yaml

# Restore to specific namespace
kubectl apply -f backup-resources.yaml -n <target-namespace>

# Verify restoration
kubectl get all -n <namespace>
```

### Disaster Recovery

**Etcd Backup (if you have access):**
```bash
# Backup etcd
ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Verify snapshot
ETCDCTL_API=3 etcdctl snapshot status /backup/etcd-snapshot.db --write-out=table
```

**Using Velero (if installed):**
```bash
# Create backup
velero backup create <backup-name> --include-namespaces <namespace>

# List backups
velero backup get

# Restore from backup
velero restore create --from-backup <backup-name>

# Check restore status
velero restore describe <restore-name>
```

---

## Useful Commands Reference

### Context and Config
```bash
# List contexts
kubectl config get-contexts

# Switch context
kubectl config use-context <context-name>

# Set default namespace
kubectl config set-context --current --namespace=<namespace>
```

### Resource Management
```bash
# Scale deployment
kubectl scale deployment <deployment-name> -n <namespace> --replicas=<count>

# Restart deployment
kubectl rollout restart deployment <deployment-name> -n <namespace>

# View rollout history
kubectl rollout history deployment <deployment-name> -n <namespace>

# Edit resource
kubectl edit <resource-type> <resource-name> -n <namespace>

# Patch resource
kubectl patch <resource-type> <resource-name> -n <namespace> -p '<json-patch>'
```

### Monitoring
```bash
# Watch resources
kubectl get pods -n <namespace> -w

# Get resource as JSON/YAML
kubectl get <resource-type> <resource-name> -n <namespace> -o yaml

# Get specific field
kubectl get <resource-type> <resource-name> -n <namespace> -o jsonpath='{.spec.field}'

# List resources with custom columns
kubectl get pods -n <namespace> -o custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName
```

---

## Escalation Guidelines

### When to Escalate

**Immediate Escalation Required:**
- Complete cluster outage
- Security breach detected
- Data loss or corruption
- Multiple node failures
- Control plane issues

**Escalation After Initial Troubleshooting:**
- Persistent performance degradation
- Recurring pod failures
- Storage issues affecting multiple applications
- Network connectivity problems affecting multiple services

### Escalation Information to Provide

1. Incident description and impact
2. Timeline of events
3. Steps already taken
4. Current cluster state
5. Relevant logs and metrics
6. Number of affected users/services

---

## Maintenance Windows

### Pre-Maintenance Checklist

- [ ] Notify stakeholders
- [ ] Backup critical data
- [ ] Document current state
- [ ] Prepare rollback plan
- [ ] Schedule appropriate window
- [ ] Verify team availability

### Post-Maintenance Checklist

- [ ] Verify all services running
- [ ] Check application functionality
- [ ] Review monitoring dashboards
- [ ] Update documentation
- [ ] Notify stakeholders of completion
- [ ] Schedule post-mortem if issues occurred

---

## Additional Resources

- Kubernetes Documentation: https://kubernetes.io/docs/
- kubectl Cheat Sheet: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- CNCF Landscape: https://landscape.cncf.io/
- Kubernetes Slack: https://kubernetes.slack.com/

---

*Last Updated: [Date]*  
*Maintained By: Cory Janowski*  
*Version: 1.0*
