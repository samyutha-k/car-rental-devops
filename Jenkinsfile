pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Run Docker Manually') {
            steps {
                sh 'docker stop car-rental || true'
                sh 'docker rm car-rental || true'
                sh 'docker build -t car-rental-app .'
                sh 'docker run -d -p 5000:5000 --name car-rental car-rental-app'
            }
        }

        stage('Verify') {
            steps {
                sh 'docker ps'
            }
        }

    }
}