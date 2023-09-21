import pulumi
import pulumi_awsx as awsx
import pulumi_eks as eks
import pulumi_kubernetes as kubernetes

config = pulumi.Config()
desired_cluster_size = config.get_int("desiredClusterSize")
if desired_cluster_size is None:
    desired_cluster_size = 1
eks_node_instance_type = config.get("eksNodeInstanceType")
if eks_node_instance_type is None:
    eks_node_instance_type = "t3.medium"
max_cluster_size = config.get_int("maxClusterSize")
if max_cluster_size is None:
    max_cluster_size = 2
min_cluster_size = config.get_int("minClusterSize")
if min_cluster_size is None:
    min_cluster_size = 1
vpc_network_cidr = config.get("vpcNetworkCidr")
if vpc_network_cidr is None:
    vpc_network_cidr = "10.0.0.0/16"
app_labels = {
    "app": "ui-app",
}
api_labels = {
    "app": "api-app",
}
eks_vpc = awsx.ec2.Vpc("eks-vpc",
    cidr_block=vpc_network_cidr,
    enable_dns_hostnames=True,
    tags={
        "project": "infra-team-test",
        "owner": "richard",
    })
eks_cluster = eks.Cluster("eks-cluster",
    desired_capacity=desired_cluster_size,
    instance_type=eks_node_instance_type,
    max_size=max_cluster_size,
    min_size=min_cluster_size,
    name="infra-team-test-cluster",
    node_associate_public_ip_address=False,
    private_subnet_ids=eks_vpc.private_subnet_ids,
    public_subnet_ids=eks_vpc.public_subnet_ids,
    vpc_id=eks_vpc.vpc_id,
    tags={
        "project": "infra-team-test",
        "owner": "richard",
    })
eks_provider = kubernetes.Provider("eks-provider", kubeconfig=eks_cluster.kubeconfig_json)
ui_repository = awsx.ecr.Repository("ui-repository",
    name="web-ui",
    tags={
        "project": "infra-team-test",
        "owner": "richard",
    })
ui_image = awsx.ecr.Image("ui-image",
    repository_url=ui_repository.url,
    path="./infra-web")
api_repository = awsx.ecr.Repository("api-repository",
    name="api-repo",
    tags={
        "project": "infra-team-test",
        "owner": "richard",
    })
api_image = awsx.ecr.Image("api-image",
    repository_url=api_repository.url,
    path="./infra-api")
infra_ns = kubernetes.core.v1.Namespace("infra-ns", opts=pulumi.ResourceOptions(provider=eks_provider))
ui_deployment = kubernetes.apps.v1.Deployment("ui-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="web-ui",
        namespace=infra_ns.metadata.name,
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels=app_labels,
        ),
        replicas=1,
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels=app_labels,
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    name="web-ui",
                    image=ui_image.image_uri,
                    ports=[kubernetes.core.v1.ContainerPortArgs(
                        name="ui",
                        container_port=5000,
                    )],
                    env=[kubernetes.core.v1.EnvVarArgs(
                        name="ApiAddress",
                        value=infra_ns.metadata.apply(lambda metadata: f"http://api-service.{metadata.name}.svc.cluster.local:5000/WeatherForecast"),
                    )],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))
web_service = kubernetes.core.v1.Service("web-service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="web-service",
        namespace=infra_ns.metadata.name,
        labels=app_labels,
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="LoadBalancer",
        selector=app_labels,
        ports=[kubernetes.core.v1.ServicePortArgs(
            port=80,
            target_port=5000,
            protocol="TCP",
        )],
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))
api_deployment = kubernetes.apps.v1.Deployment("api-deployment",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="web-api",
        namespace=infra_ns.metadata.name,
    ),
    spec=kubernetes.apps.v1.DeploymentSpecArgs(
        selector=kubernetes.meta.v1.LabelSelectorArgs(
            match_labels=api_labels,
        ),
        replicas=1,
        template=kubernetes.core.v1.PodTemplateSpecArgs(
            metadata=kubernetes.meta.v1.ObjectMetaArgs(
                labels=api_labels,
            ),
            spec=kubernetes.core.v1.PodSpecArgs(
                containers=[kubernetes.core.v1.ContainerArgs(
                    name="web-api",
                    image=api_image.image_uri,
                    ports=[kubernetes.core.v1.ContainerPortArgs(
                        name="api",
                        container_port=5000,
                    )],
                )],
            ),
        ),
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))
api_service = kubernetes.core.v1.Service("api-service",
    metadata=kubernetes.meta.v1.ObjectMetaArgs(
        name="api-service",
        namespace=infra_ns.metadata.name,
        labels=api_labels,
    ),
    spec=kubernetes.core.v1.ServiceSpecArgs(
        type="ClusterIP",
        selector=api_labels,
        ports=[kubernetes.core.v1.ServicePortArgs(
            port=5000,
            target_port=5000,
            protocol="TCP",
        )],
    ),
    opts=pulumi.ResourceOptions(provider=eks_provider))
pulumi.export("ui-url", web_service.status.load_balancer.ingress[0].hostname)
