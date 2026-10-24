pipeline {
    agent any
    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }
    parameters {
        string(name: 'DEPLOY_HOST', defaultValue: '192.168.64.10', description: 'IP Ubuntu-сервера; пример нужно заменить')
        choice(name: 'TARGET_PLATFORM', choices: ['linux/amd64', 'linux/arm64'], description: 'x86_64 = amd64, aarch64 = arm64')
    }
    environment {
        PATH = "/opt/homebrew/bin:/usr/local/bin:/Applications/Docker.app/Contents/Resources/bin:${env.PATH}"
        IMAGE_NAME = 'project-forms'
        IMAGE_ARCHIVE = 'project-forms-image.tar'
    }
    stages {
        stage('1. Checkout from GitHub') {
            steps { checkout scm }
        }
        stage('2. Build Docker image') {
            steps {
                sh '''
                    set -eu
                    docker build --platform "$TARGET_PLATFORM" -t "$IMAGE_NAME:$BUILD_NUMBER" .
                    docker save --output "$IMAGE_ARCHIVE" "$IMAGE_NAME:$BUILD_NUMBER"
                    ls -lh "$IMAGE_ARCHIVE"
                '''
            }
        }
        stage('3. Ansible transfer and deploy') {
            steps {
                withCredentials([sshUserPrivateKey(
                    credentialsId: 'lab4-server-ssh',
                    keyFileVariable: 'SSH_KEY',
                    usernameVariable: 'SSH_USER'
                )]) {
                    sh '''
                        set -eu
                        # Только для изолированной учебной VM (в продакшене нужен known_hosts)
                        export ANSIBLE_HOST_KEY_CHECKING=False
                        ansible-playbook \
                            -i "${DEPLOY_HOST}," \
                            -u "$SSH_USER" \
                            --private-key "$SSH_KEY" \
                            -e "image_archive=$WORKSPACE/$IMAGE_ARCHIVE" \
                            -e "image_name=$IMAGE_NAME" \
                            -e "image_tag=$BUILD_NUMBER" \
                            ansible/deploy.yml
                    '''
                }
            }
        }
    }
    post {
        always { sh 'rm -f "$IMAGE_ARCHIVE"' }
        success { echo "Deployed: http://${params.DEPLOY_HOST}:8000/" }
    }
}
