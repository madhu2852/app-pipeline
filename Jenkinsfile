import groovy.json.JsonOutput
import groovy.json.JsonSlurperClassic



pipeline {
    agent any
    options {
        timestamps()
        buildDiscarder(logRotator(daysToKeepStr: '90'))
        disableConcurrentBuilds()
    }
    environment {
        AWS_ACCESS_KEY_ID = credentials('secret-key-id')
        AWS_SECRET_ACCESS_KEY = credentials('access-key') 
        available_port = """${sh(
                returnStdout: true,
                script: '''
                    set +x
                    export PATH=~/.local/bin:$PATH
                    pip3 install pipenv --user > /dev/null
                    pipenv update > /dev/null
                    pipenv run python3 ./queryitem.py
                '''    
            )}"""
    }
    parameters {
        string(
            name: 'app_name',
            description: 'application Name',
            trim: true,
        )
        string(
            name: 'app_owner',
            description: '''application owner''',
        )
        string(
            name: 'app_owner_email',
            description: 'Email Address - required',
            trim: true,
        )
        string(
            name: 'app_cert_arn',
            description: 'Cert ARN - required',
            trim: true,
        )
        choice(
            name: 'env',
            choices: ['dev', 'stg', 'prd'],
            description: '''Jenvironment to deploy the app''',
        )        

    }
    stages {        
        stage('get port number from ddb_Table') {
            steps {
                sh '''
                    export port_num=$available_port
                    echo "here is the number: $port_num"
                    '''
                }
            }
        stage('Create AWS ELB resources for the app') {
            steps {
                script {
                    cleanWs()
                }
            }
        }
        stage('update dynamodb table with app metadata') {
            steps {
                script {
                    cleanWs()
                }
            }
        }
    }    
}
