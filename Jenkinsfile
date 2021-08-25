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
        // string(
        //     name: 'LISTENER_ARN',
        //     description: '''application owner''',
        // )        
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
                INTERNAL_APP_CERTIFICATE_TAG_NAME = """${sh(
                returnStdout: true,
                script: '''
                    terraform output public_elb
                '''    
            ).trim()}"""
            }
            
            steps {
                sh '''
                    set +x
                    export PATH=~/.local/bin:$PATH
                    pip3 install pipenv --user > /dev/null
                    pipenv update > /dev/null
                    pipenv run python3 ./updateitem.py provision $TF_VAR_available_port ${INTERNAL_APP_CERTIFICATE_TAG_NAME}
                    '''
                }
            }
        stage('clean up jenkins workspace') {
            steps {
                sh ''' echo "works great!" '''
            }
        }
    }    
}
