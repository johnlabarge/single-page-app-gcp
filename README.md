# Single Page App on GCP 

## Architectural Overview 

This is a tutorial for how to get up and running with your own Single Page application and API on GCP quickly.  Single Page Apps are web apps that load a single HTML page and dynamically update that page as the user interacts with the application. The browser based applicaiton makes API calls in JavaScript back to the API.  This tuotrial assumes that the API is using a different domain and as a result uses [Cross Origin Resource Sharing](https://en.wikipedia.org/wiki/Cross-origin_resource_sharing). 

The static web pages rely on Cloud Storage and Cloud CDN (provided by Firebase Hosting). And the tutorial provides optional instructions for setting up your custom domain to work withn Firebase Hosting. 

This GCP architecture relies on Cloud Load Balancing, Identity Aware Proxy, Kubernetes Engine and optionally Cloud DNS.  Within Kubernetes Engine the architecture includes Elasticsearch, [Extensible Service Proxy](https://github.com/cloudendpoints/esp) and cert-manager.  In addition, the Kubernetes Engine architecture makes use of custom  resource definitions and controllers for deploying the Cloud Endpoints Service.  Finally, the tutorial makes heave use of helm for isntalling Kubernetes components in addition to some kubectl plugis intended to help speed things along. 

![Architecture](https://github.com/johnlabarge/single-page-app-gcp/raw/master/spa_overview.png)

 
