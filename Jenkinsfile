pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "dogexpress_tests:latest" // Name for the Docker image
        // Define volume mounts inside the stage to avoid any confusion with paths
        // DOCKER_VOLUMES = '-v C:/ProgramData/Jenkins/.jenkins/workspace/Dogexpress:/workspace/tests'
    }

    stages {
        stage('Checkout') {
            steps {
                // Checkout code from Git
                git branch: 'main', url: 'https://github.com/sk-primotech/dogexpress.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                bat '''
                REM Install required Python dependencies
                C:\\Users\\Sarvesh\\AppData\\Local\\Programs\\Python\\Python311\\python.exe -m pip install --upgrade pip
                C:\\Users\\Sarvesh\\AppData\\Local\\Programs\\Python\\Python311\\Scripts\\pip.exe install -r requirements.txt
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build Docker image for the test environment
                    docker.build(env.DOCKER_IMAGE)
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    // Run the Docker image and execute tests
                    docker.image(env.DOCKER_IMAGE).inside(env.DOCKER_VOLUMES) {
                        bat 'pytest --alluredir=allure-results'
                    }
                }
            }
        }

        stage('Generate Allure Report') {
            steps {
                allure([
                    results: [[path: 'allure-results']],
                    reportBuildPolicy: 'ALWAYS'
                ])
            }
        }
    }

    post {
        always {
            // Archive test results
            archiveArtifacts artifacts: 'allure-results/**', allowEmptyArchive: true

            // Publish Allure report
            allure([
                results: [[path: 'allure-results']],
                reportBuildPolicy: 'ALWAYS'
            ])
        }
    }
}
