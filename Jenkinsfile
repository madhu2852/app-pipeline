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
    }
    parameters {
        string(
            name: 'APP_FQDN',
            description: 'application fqdn',
            trim: true,
        )
        string(
            name: 'INTERNAL_APP_CERTIFICATE_TAG_NAME',
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
            description: '''environment to deploy the app''',
        )
    }
    stages {        
        stage('Preparation') {
            steps {
                script {
                    env.TF_VAR_APP_FQDN = env.APP_FQDN
                    env.TF_VAR_CONTACT = env.CONTACT
                    env.TF_VAR_INTERNAL_APP_CERTIFICATE_TAG_NAME = env.INTERNAL_APP_CERTIFICATE_TAG_NAME
                    switch(env.ENVIRONMENT) {
                        case 'DEV':
                            env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-dev"
                            env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-dev"
                            break
                        case 'STG':
                            env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-stg"
                            env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-stg"
                            break
                        case 'PRD':
                            env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-prd"
                            env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-prd"
                            break
                        default:
                            error('Listener ARN Required')
                    }
                }
            }
        } 
        stage('Configure AWS Services (terraform apply)') {
            environment {
                
                TF_VAR_available_port = """${sh(
                    returnStdout: true,
                    script: '''
                        set +x
                        export PATH=~/.local/bin:$PATH
                        pip3 install pipenv --user > /dev/null
                        pipenv update > /dev/null
                        pipenv run python3 ./queryitem.py
                    '''    
                        ).trim()}"""
                }
            
            steps {
                sh '''
                    env 
                    terraform init &&\
                    terraform apply --auto-approve
                    #terraform refresh
                    '''
                }
            }
        stage('add metadata and reserve port in Dynamodb Table') {
            
            environment {
                
                PUBLIC_ALB_ARN = """${sh(
                returnStdout: true,
                script: '''
                    terraform output -json public_elb | jq -r '.[0]'
                '''    
            ).trim()}"""
            
                INTERNAL_CERT_ARN = """${sh(
                returnStdout: true,
                script: '''
                    terraform output -json internal_app_cert | jq -r '.[0]'
                '''    
            ).trim()}"""
            
                PUBLIC_ALB_LISTENER = """${sh(
                returnStdout: true,
                script: '''
                    terraform output -json public_elb_lstnr | jq -r '.[0]'
                '''    
            ).trim()}"""
  
            }
            
            steps {
                sh '''
                    set +x
                    export PATH=~/.local/bin:$PATH
                    pip3 install pipenv --user > /dev/null
                    pipenv update > /dev/null
                    pipenv run python3 ./updateitem.py provision $TF_VAR_available_port ${PUBLIC_ALB_LISTENER}
                    '''
                }
            }
        }
    post {
        cleanup {
            cleanWs(cleanWhenAborted: false)
        }
    }    
}
