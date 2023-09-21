# Setup

Ensure you have [pulumi](https://www.pulumi.com/docs/clouds/aws/get-started/begin/), [awscli](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) and [kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html) configured on your machine.

Clone this git repository 
```
git clone https://github.com/rolani/infra-team-test.git
```

# How to run
Change current directory to the cloned repo
```
cd infra-team-test
```
Deploy the infrastructure and applications to AWS EKS using pulumi
```
make deploy
```
Alternatively run:
```
pulumi up -s production --yes
```
The above command will output the load-balancer url for the web ui that entered in a browser.

# Application Details

- All resources deployed on AWS have the following tags

  `project: infra-team-test`

  `owner: richard`
- The web API is deployed as a deployment on the EKS cluster on a node in a private subnet. 
- The web API service uses a `ClusterIP` and thus it cannot be accessed from outside the cluster.
- The UI is likewise deployed on a node in a private subnet on the EKS cluster.
- The UI is exposed to the public internet through a `LoadBalancer` service



# Cleanup

Run the following command to clean up/destroy all the created resources:
```
make destroy
```
Alternatively run:
```
pulumi destroy -s production --yes
```