pipeline {
    agent any

    environment {
        IMAGE_NAME = "rakesh6nm/flask-app"
        TAG = "${BUILD_NUMBER}"

        GIT_REPO = "https://github.com/rakesh611/Hotel_Reservation_Prediction.git"

        GITOPS_REPO = "https://github.com/rakesh611/flask-k8s-manifests.git"
        GITOPS_DIR = "flask-k8s-manifests"
    }

    options {
        skipDefaultCheckout()
        timestamps()   // ✅ Better logging
    }

    stages {

        stage('🧹 Clean Workspace') {
            steps {
                deleteDir()
            }
        }

        stage('📥 Clone Application Repo') {
            steps {
                git branch: 'main', url: "${GIT_REPO}"
            }
        }

        stage('🐳 Build Docker Image') {
            steps {
                echo "Building Docker image: ${IMAGE_NAME}:${TAG}"
                sh """
                    docker build -t ${IMAGE_NAME}:${TAG} .
                """
            }
        }

        stage('🔐 Security Scan (Trivy)') {
            steps {
                echo "Running Trivy scan..."
                sh """
                    trivy image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:${TAG}
                """
            }
        }

        stage('🔑 Docker Login') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-token', variable: 'DOCKER_TOKEN')]) {
                    sh '''
                        echo $DOCKER_TOKEN | docker login -u rakesh6nm --password-stdin
                    '''
                }
            }
        }

        stage('📤 Push Docker Image') {
            steps {
                sh """
                    docker push ${IMAGE_NAME}:${TAG}
                    docker tag ${IMAGE_NAME}:${TAG} ${IMAGE_NAME}:latest
                    docker push ${IMAGE_NAME}:latest
                """
            }
        }

        stage('📥 Clone GitOps Repo') {
            steps {
                dir("${GITOPS_DIR}") {
                    git branch: 'main',
                        url: "${GITOPS_REPO}",
                        credentialsId: 'github-creds'
                }
            }
        }

        stage('✏️ Update Kubernetes Manifest') {
            steps {
                dir("${GITOPS_DIR}") {
                    withCredentials([usernamePassword(
                        credentialsId: 'github-creds',
                        usernameVariable: 'GIT_USER',
                        passwordVariable: 'GIT_PASS'
                    )]) {
                        sh """
                            echo "Updating deployment.yaml with new image"

                            # ✅ safer replacement (only change image line)
                            sed -i 's|image: .*|image: ${IMAGE_NAME}:${TAG}|g' deployment.yaml

                            git config user.email "jharakesh485@gmail.com"
                            git config user.name "Rakesh"

                            git add deployment.yaml
                            git commit -m "Update image to version ${TAG}" || echo "No changes to commit"

                            git push https://${GIT_USER}:${GIT_PASS}@github.com/rakesh611/flask-k8s-manifests.git
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            cleanWs()   // ✅ cleanup after build
        }
        success {
            echo "✅ Pipeline completed successfully!"
        }
        failure {
            echo "❌ Pipeline failed! Check logs."
        }
    }
}
