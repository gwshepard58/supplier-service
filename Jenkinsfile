node {
    def appName = 'supplier-service'
    def imageName = 'supplier-service:latest'
    def namespace = 'ea2sa-services'
    def deploymentFile = 'k8s/deployment.yaml'
    def serviceFile = 'k8s/service.yaml'

    stage('Checkout') {
        checkout([$class: 'GitSCM',
            branches: [[name: '*/main']],
            userRemoteConfigs: [[url: 'https://github.com/gwshepard58/supplier-service.git']]
        ])
    }

    stage('Install Dependencies') {
        echo 'Installing Node.js dependencies...'
        sh 'npm install'
    }

    stage('Build Docker Image') {
        echo 'Building Docker image...'
        sh 'eval $(minikube docker-env) && docker build -t ' + imageName + ' .'
    }

    stage('Apply Kubernetes Deployment') {
        echo 'Deploying to Minikube...'
        sh "kubectl apply -f ${deploymentFile} --namespace=${namespace}"
        sh "kubectl apply -f ${serviceFile} --namespace=${namespace}"
    }

    stage('Verify Deployment') {
        echo 'Waiting for rollout to complete...'
        sh "kubectl rollout status deployment/${appName} --namespace=${namespace}"
    }
}
