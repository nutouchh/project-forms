pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        PATH = "/opt/homebrew/bin:/usr/local/bin:/Applications/Docker.app/Contents/Resources/bin:${env.PATH}"
        IMAGE_NAME = 'project-forms'
        CONTAINER_NAME = 'project-forms-app'
    }

    stages {
        stage('1. Checkout from GitHub') {
            steps {
                checkout scm
            }
        }

        stage('2. Build Docker image') {
            steps {
                sh 'docker build -t "$IMAGE_NAME:$BUILD_NUMBER" -t "$IMAGE_NAME:latest" .'
            }
        }

        stage('3. Deploy container') {
            steps {
                sh '''
                    if docker container inspect "$CONTAINER_NAME" >/dev/null 2>&1; then
                        docker rm -f "$CONTAINER_NAME"
                    fi
                    docker run -d \
                        --name "$CONTAINER_NAME" \
                        --restart unless-stopped \
                        -p 5000:5000 \
                        -v project-forms-data:/app/data \
                        "$IMAGE_NAME:latest"
                '''
            }
        }

        stage('4. Verify application') {
            steps {
                sh '''
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if curl --fail --silent --output /dev/null http://127.0.0.1:5000/; then
                            echo 'Application is available at http://localhost:5000'
                            exit 0
                        fi
                        sleep 2
                    done
                    docker logs "$CONTAINER_NAME"
                    exit 1
                '''
            }
        }
    }
}
