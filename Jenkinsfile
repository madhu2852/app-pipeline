import groovy.json.JsonOutput
import groovy.json.JsonSlurperClassic

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
        stage('get Available Port Number From Dynamodb Table') {
            environment {
                env = "${JENKINS_USER_ID}"
                ddb_Table = "${PATH_PREFIX}"
            }
            steps {
                    sh '''
                        export PATH=~/.local/bin:$PATH
                        pip3 install pipenv --user
                    '''
            }
        }
        stage('hello AWS') {
            steps {
                withAWS(credentials: 'aws-credentials', region: 'us-east-1') {
                    sh '''
                    aws dynamodb query \
                        --table-name dev-ports \
                        --index-name StateIndex \
                        --key-condition-expression "port_state = a"
                    '''    
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