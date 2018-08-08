# Single Page App on GCP 

## Architectural Overview 

This is a tutorial for how to get up and running with your own Single Page application and API on GCP quickly.  Single Page Apps are web apps that load a single HTML page and dynamically update that page as the user interacts with the application. The browser based applicaiton makes API calls in JavaScript back to the API.  This tuotrial assumes that the API is using a different domain and as a result uses [Cross Origin Resource Sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing). 

From a high level, the static web pages rely on Cloud Storage and Cloud CDN (provided by Firebase Hosting), while the API is hosted in Kubernetes.  

![Architecture](https://github.com/johnlabarge/single-page-app-gcp/raw/master/spa_overview.png)

 
## Deploying the API 

### API Architecture   
The underlying API is deployed to Kubernetes Engine and load balanced using a [Cloud Load Balancing](https://cloud.google.com/load-balancing/) which is added using a Kubernetes ingress object. In this case implemented using [Elasticsearch](https://www.elastic.co/) with CORS enabled (installable via a [helm](https://helm.sh/) chart).  However, because the API will be exposed directly to the single page web application (SPA) via the public internet it requires additional security.  [Cloud Endpoints](https://cloud.google.com/endpoints/) is used to validate authentication to the API inside the Kubernetes cluster and could be used to throttle requests if necessary (though this is out of scope for this tutorial).  [Identity Aware Proxy](https://cloud.google.com/iap/) is used for authentication and authorization of the user. [Identity Aware Proxy](https://cloud.google.com/iap/) is configured using [Cloud Identity and Acccess Management](https://cloud.google.com/iam/docs/).  

![API Architecture](https://github.com/johnlabarge/single-page-app-gcp/raw/master/spa-api.png)

### Kubernetes Environment
The Kubernetes environment is enhanced for this tutuorial in a couple of ways outside the normal course of deploying the required components. First, you'll install [helm](https://helm.sh/) which will make it easier to deploy many of the Kubernetes components for this tutorial.  Using [helm](https://helm.sh/) you'll add a custom resource definiton and controller for deploying the Cloud Endpoints and associating it with ingress objects. Finally, you'll install a suite of kubectl plugis to help with some of the commands. 


[![button](http://gstatic.com/cloudssh/images/open-btn.png)](https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/johnlabarge/single-page-app-gcp&page=editor&tutorial=README.md)

## Task 0 - Setup environment

1. Set the project, replace `YOUR_PROJECT` with your project ID:

```
gcloud config set project YOUR_PROJECT
```

2. Install kubectl plugins:

```
mkdir -p ~/.kube/plugins
git clone https://github.com/danisla/kubefunc.git ~/.kube/plugins/kubefunc
```

3. Create GKE cluster:

```
VERSION=$(gcloud container get-server-config --zone us-central1-f --format='value(validMasterVersions[0])')
gcloud container clusters create dev --zone=us-central1-c --cluster-version=${VERSION} --scopes=cloud-platform
```

4. Install helm

```
kubectl plugin install-helm
```

5. Install Cloud Endpoints Controller

```
kubectl plugin install-cloud-endpoints-controller
```

## Task 1 - Deploy Elastic Search

1. helm repo add incubator http://storage.googleapis.com/kubernetes-charts-incubator
2. helm install --name spa-search-api incubator/elasticsearch -f api/es-values.yml
3. Verify elastic search is running #TODO
4. Build Elastic Search Index

## Task 3 - Configure OAuth consent screen

1. Go to the [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2. Under __Email address__, select the email address you want to display as a public contact. This must be your email address, or a Google Group you own.
3. Enter the __Product name__ you would like to display.
4. Add any optional details you’d like.
5. Click __Save__.

## Task 4 - Set up IAP access

1. Go to the [Identity-Aware Proxy page](https://console.cloud.google.com/security/iap/project).
2. On the right side panel, next to __Access__, click __Add__.
3. In the __Add members__ dialog that appears, add the email addresses of groups or individuals to whom you want to grant the __IAP-Secured Web App User__ role for the project

    The following kinds of accounts can be members:
    - __Google Accounts__: user@gmail.com
    - __Google Groups__: admins@googlegroups.com
    - __Service accounts__: server@example.gserviceaccount.com
    - __G Suite domains__: example.com

    Make sure to add a Google account that you have access to.


## Task 6 - Deploy iap-ingress chart

3. Create values file for chart:


```
cat > iap-values.yaml <<EOF
projectID: $(gcloud config get-value project)
endpointServiceName: spa-api
targetServiceName: search-api
targetServicePort: 8080
oauthSecretName: iap-oauth
tlsSecretName: iap-tutorial-ingress-tls
esp:
  enabled: true
EOF
```

2. Deploy chart to create IAP aware ingress resource:

```
 helm github install \
    --name api-iap \
    --repo https://github.com/danisla/cloud-endpoints-controller.git \
    --ref master \
    --path examples/iap-esp/charts/iap-ingress
    -f iap-values.yaml
```

3. Wait for the load balancer to be provisioned:

```
PROJECT=$(gcloud config get-value project)
COMMON_NAME="spa-api.endpoints.${PROJECT}.cloud.goog"

(until [[ $(curl -sfk -w "%{http_code}" https://${COMMON_NAME}) == "302" ]]; do echo "Waiting for LB with IAP..."; sleep 2; done)
```


## Task 5 Deploy 
4. Open your browser to `https://spa-api.endpoints.PROJECT_ID.cloud.goog` replacing `PROJECT_ID` with your project id.
5. Login with your Google account and verify the the sample app is show.

> NOTE: It may take 10-15 minutes for the load balancer to be provisioned.

## Task 6 - Cleanup

1. Delete the chart:

```
helm delete --purge spa-search-api
kubectl delete pvc -l release=my-release,component=data
helm delete --purge iap-tutorial-ingress
```

> This will trigger the load balancer cleanup. Wait a few moments before continuing.

2. Delete the GKE cluster:

```
gcloud container clusters delete dev --zone us-central1-c
```
