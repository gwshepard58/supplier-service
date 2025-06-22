node {
    def appName = 'supplier-service'
    def imageName = 'supplier-service:latest'

    stage('Checkout') {
        echo '📦 Cloning repository...'
        git url: 'https://github.com/gwshepard58/supplier-service.git', branch: 'main'
    }

    stage('Build Docker Image') {
        echo '🐳 Building Docker image...'
        sh 'eval $(minikube docker-env) && docker build -t supplier-service:latest .'
    }

    stage('Install Dependencies') {
        echo '🔧 Skipped: Node.js not configured yet. Placeholder for npm install.'
    }

    stage('Kubernetes Deployment') {
        echo '🚀 Placeholder: Apply Kubernetes manifests (deployment.yaml, service.yaml)'
    }

    stage('Verify Rollout') {
        echo '✅ Placeholder: Verify Kubernetes rollout status'
    }
}
