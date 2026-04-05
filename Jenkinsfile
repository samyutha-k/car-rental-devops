pipeline {
    agent any

    stages {
        stage('Clone Repo') {
            steps {
                git 'https://github.com/Medhuna/car-rental.git'
            }
        }

        stage('Build Docker') {
            steps {
                sh 'docker-compose build'
            }
        }

        stage('Run Containers') {
            steps {
                sh 'docker-compose up -d'
            }
        }
    }
}