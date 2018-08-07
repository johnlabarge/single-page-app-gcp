# Single Page App on GCP 

## Architectural Overview 

This is a tutorial for how to get up and running with your own Single Page application and API on GCP quickly.  Single Page Apps are web apps that load a single HTML page and dynamically update that page as the user interacts with the application. The browser based applicaiton makes API calls in JavaScript back to the API.  This tuotrial assumes that the API is using a different domain and as a result uses [Cross Origin Resource Sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing). 

From a high level, the static web pages rely on Cloud Storage and Cloud CDN (provided by Firebase Hosting), while the API is hosted in Kubernetes.  

![Architecture](https://github.com/johnlabarge/single-page-app-gcp/raw/master/spa_overview.png)

 
## Deploying the API 

Below is the architecture of the API that will be deployed to kubernetes. 

### API Architecture   
The underlying API is deployed to Kubernetes Engine and load balanced using a [Cloud Load Balancing](https://cloud.google.com/load-balancing/) which is added using a Kubernetes ingress object. In this case implemented using [Elasticsearch](https://www.elastic.co/) with CORS enabled (installable via a [helm](https://helm.sh/) chart).  However, because the API will be exposed directly to the single page web application (SPA) via the public internet it requires additional security.  [Cloud Endpoints](https://cloud.google.com/endpoints/) is used to validate authentication to the API inside the Kubernetes cluster and could be used to throttle requests if necessary (though this is out of scope for this tutorial).  [Identity Aware Proxy](https://cloud.google.com/iap/) is used for authentication and authorization of the user. [Identity Aware Proxy](https://cloud.google.com/iap/) is configured using [Cloud Identity and Acccess Management](https://cloud.google.com/iam/docs/).  

![API Architecture](https://github.com/johnlabarge/single-page-app-gcp/raw/master/spa-api.png)

### Kubernetes Environment
The Kubernetes environment is enhanced for this tutuorial in a couple of ways outside the normal course of deploying the required components. First, you'll install [helm](https://helm.sh/) which will make it easier to deploy many of the Kubernetes components for this tutorial.  Using [helm](https://helm.sh/) you'll add a custom resource definiton and controller for deploying the Cloud Endpoints and associating it with ingress objects. Finally, you'll install a suite of kubectl plugis to help with some of the commands. 

