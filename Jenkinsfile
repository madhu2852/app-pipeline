import groovy.json.JsonOutput
import groovy.json.JsonSlurperClassic

String listern_arn_pub_alb_dev = 'testarn'

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
        TF_VAR_available_port = """${sh(
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
            choices: ['dev', 'stg', 'prd'],
            description: '''environment to deploy the app''',
        )
    }
    stages {        
        stage('Preparation') {
            steps {
                script {
                    env.TF_VAR_APP_FQDN = env.APP_FQDN
                    env.TF_VAR_CONTACT = env.CONTACT
                    env.TF_VAR_CERTIFICATE_ARN = env.CERTIFICATE_ARN
                    switch(env.ENVIRONMENT) {
                        case 'DEV':
                            env.TF_VAR_LISTENER_ARN = "${listern_arn_pub_alb_dev}"
                            break
                        case 'STG':
                            env.TF_VAR_LISTENER_ARN = "${listern_arn_pub_alb_stg}"
                            break
                        case 'PRD':
                            env.TF_VAR_LISTENER_ARN = "${listern_arn_pub_alb_prd}"
                            break
                        default:
                            error('Listener ARN Required')
                    }
                }
            }
        } 
        stage('Configure AWS Services (terraform apply)') {
            steps {
                sh '''
                    env 
                    terraform plan
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
                    pipenv run python3 ./updateitem.py provision $TF_VAR_available_port ${TF_VAR_APP_FQDN}
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
