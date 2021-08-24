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
            name: 'APP_FQDN',
            description: 'application fqdn',
            trim: true,
        )
        string(
            name: 'CERTIFICATE_ARN',
            description: '''application owner''',
        )
        string(
            name: 'CONTACT',
            description: 'Email Address - required',
            trim: true,
        )
        choice(
            name: 'ENVIRONMENT',
            choices: ['DEV', 'STG', 'PRD'],
            description: '''Jenvironment to deploy the app''',
        )
    }
    stages {        
        stage('Preparation') {
            steps {
                script {
                    env.APP_FQDN = env.APP_FQDN
                    env.CONTACT = env.CONTACT
                    env.CERTIFICATE_ARN = env.CERTIFICATE_ARN
                }
            }
        }        
        stage('Configure AWS Services (terraform apply)') {
            steps {
                sh '''
                    export port_num=$available_port
                    echo "here is the number: $port_num"
                    '''
                }
            }
        stage('add metadata and reserve port in Dynamodb Table') {
            steps {
                sh '''
                    set +x
                    export PATH=~/.local/bin:$PATH
                    pip3 install pipenv --user > /dev/null
                    pipenv update > /dev/null
                    pipenv run python3 ./updateitem.py provision $available_port ${APP_FQDN}
                    '''
                }
            }
        stage('clean up jenkins workspace') {
            steps {
                script {
                    cleanWs()
                }
            }
        }
    }    
}
