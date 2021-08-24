pipeline {
    agent any 
    environment {
        AWS_ACCESS_KEY_ID = credentials('secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('access-key') 

        CC = """${sh(
                returnStdout: true,
                script: '''
                    export PATH=~/.local/bin:$PATH
                    pip3 install pipenv --user
                    pipenv update
                    pipenv run python3 ./queryitem.py
                '''    
            )}""" 
        // Using returnStatus
        EXIT_STATUS = """${sh(
                returnStatus: true,
                script: 'exit 1'
            )}"""
    }
    stages {
        stage('Example') {
            environment {
                DEBUG_FLAGS = '-g'
            }
            steps {
                sh 'printenv'
            }
        }
    }
}
