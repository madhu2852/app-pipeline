import groovy.json.JsonOutput
import groovy.json.JsonSlurperClassic

String PORT_NUM = null

pipeline {
    agent any
    options {
        timestamps()
        buildDiscarder(logRotator(daysToKeepStr: '90'))
        disableConcurrentBuilds()
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
    // environment {
    // }
    stages {        
        stage('get port number from ddb_Table') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                    PORT_NUM = sh(script: '''
                        export PATH=~/.local/bin:$PATH
                        pip3 install pipenv --user
                        pipenv update
                        PORT_NUM=$(pipenv run python3 ./queryitem.py)
                        echo $PORT_NUM
                    ''',
                    returnStdout: true
                    ).trim()
                    echo "${PORT_NUM}"
                }
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
