pipeline {
    agent any
    environment {
        IMAGE = "sandeep262005/bluegreen-app:${BUILD_NUMBER}"
    }
    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build Docker Image') {
            steps { sh 'docker build -t $IMAGE .' }
        }
        stage('Push to Docker Hub') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds',
                        usernameVariable: 'USER', passwordVariable: 'PASS')]) {
                    sh 'echo $PASS | docker login -u $USER --password-stdin'
                    sh 'docker push $IMAGE'
                }
            }
        }
        stage('Find Live Colour') {
            steps {
                script {
                    def live = sh(script: "kubectl get svc bg-service -o jsonpath='{.spec.selector.color}' 2>/dev/null || true",
                                  returnStdout: true).trim()
                    if (live == 'blue') { env.LIVE = 'blue'; env.NEW = 'green' }
                    else if (live == 'green') { env.LIVE = 'green'; env.NEW = 'blue' }
                    else { env.LIVE = 'none'; env.NEW = 'blue' }
                    echo "Currently LIVE: ${env.LIVE}  -->  Deploying new version to: ${env.NEW}"
                }
            }
        }
        stage('Deploy to Idle Environment') {
            steps {
                sh '''
                  sed -e "s|IMAGE_PLACEHOLDER|$IMAGE|g" \
                      -e "s|COLOR_PLACEHOLDER|$NEW|g" \
                      -e "s|VERSION_PLACEHOLDER|$BUILD_NUMBER|g" \
                      k8s/deployment.yaml > deploy-$NEW.yaml
                  kubectl apply -f deploy-$NEW.yaml
                  kubectl rollout status deployment/bg-app-$NEW --timeout=120s
                '''
            }
        }
        stage('Smoke Test') {
            steps {
                sh '''
                  POD_IP=$(kubectl get pods -l app=bg-app,color=$NEW -o jsonpath='{.items[0].status.podIP}')
                  echo "Testing $NEW environment at $POD_IP"
                  curl -s --max-time 10 http://$POD_IP:5000 | grep -i "$NEW"
                  echo "Smoke test PASSED"
                '''
            }
        }
        stage('Switch Traffic') {
            steps {
                sh '''
                  sed "s|COLOR_PLACEHOLDER|$NEW|g" k8s/service.yaml | kubectl apply -f -
                  echo "Traffic switched to $NEW"
                  kubectl get deployments -l app=bg-app
                  kubectl get svc bg-service -o wide
                '''
            }
        }
    }
    post {
        success { echo "SUCCESS: ${env.NEW} is LIVE. ${env.LIVE} kept for rollback. Open http://23.22.76.155:30080" }
        failure { echo "FAILED: traffic was NOT switched, users still on ${env.LIVE}" }
    }
}
