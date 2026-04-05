pipeline {
    agent any

    stage('Clone Repo') {
    steps {
        git branch: 'main', url: 'https://github.com/samyutha-k/car-rental-devops.git'
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