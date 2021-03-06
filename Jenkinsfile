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
        REGION = "us-east-1"
        PIP_ENV = """${sh(
                    returnStdout: true,
                    script: '''
                        set +x
                        export PATH=~/.local/bin:$PATH
                        pip3 install pipenv --user > /dev/null
                        pipenv update > /dev/null
                        pipenv install boto3 > /dev/null
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
            name: 'APP_CERT_NAME',
            description: '''application certificate name - use Tag Name: Value''',
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
        choice(
            name: 'ACTION',
            choices: ['', 'PROVISION', 'DECOMMISSION'],
            description: '''YES: Created Objects. NO: Deletes Objects based on APP FQDN''',
        )
    }
    stages {
        stage('set up aws credentials based on branch') {
            steps {
                script {
                    switch(env.GIT_BRANCH) {
                        case 'origin/develop':
                            credential_id = 'dev-user-creds'
                            break
                        case 'origin/stage':
                            credential_id = 'stg-user-creds'
                            break                            
                        case 'origin/master':
                            credential_id = 'prd-user-creds'
                            break                            
                        default:
                            error('Invalid Branch:' + ${env.GIT_BRANCH})
                            break
                    }
                    withCredentials([[
                        $class: 'AmazonWebServicesCredentialsBinding',
                        credentialsId: credential_id,
                        accessKeyVariable: 'AWS_ACCESS_KEY_ID',
                        secretKeyVariable: 'AWS_SECRET_ACCESS_KEY'
                    ]]) {
                        println "Setting up environment"
                        sh """
                            aws configure set aws_access_key_id ${AWS_ACCESS_KEY_ID}
                            aws configure set aws_secret_access_key ${AWS_SECRET_ACCESS_KEY}
                            aws configure set region ${REGION}
                        """
                    }
                    println "AWS  Credential Setup Completed"
                }
            }
        }      
        stage('Deploy to AWS') {
            when { expression { params.ACTION == "PROVISION" } }
            stages {
                stage('Preparation') {
                    input { message "Approve to CREATE Pub ELB Objects in AWS" }
                    steps {
                        script {
                            env.TF_VAR_APP_FQDN = env.APP_FQDN
                            env.TF_VAR_CONTACT = env.CONTACT
                            env.TF_VAR_APP_CERT_NAME = env.APP_CERT_NAME
                            switch(env.ENVIRONMENT) {
                                case 'DEV':
                                    env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-dev"
                                    env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-dev"
                                    env.DDB_TABLE = "dynamoDB-dev"
                                    break
                                case 'STG':
                                    env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-stg"
                                    env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-stg"
                                    env.DDB_TABLE = "dynamoDB-stg"
                                    break
                                case 'PRD':
                                    env.TF_VAR_PUBLIC_ALB_NAME = "public-alb-prd"
                                    env.TF_VAR_PUBLIC_ALB_LSTNR_NAME = "public-alb-lstnr-prd"
                                    env.DDB_TABLE = "dynamoDB-prd"                        
                                    break
                                default:
                                    error('Listener ARN Required')
                            }
                        }
                    }
                } 
                stage('Validate AWS Services (terraform plan)') {
                    environment {
                        TF_VAR_available_port = """${sh(
                            returnStdout: true,
                            script: '''
                                set +x
                                export PATH=~/.local/bin:$PATH
                                pipenv run python3 ./queryitem.py --env=${ENVIRONMENT} --region=${REGION} --table_name=${DDB_TABLE}
                            '''    
                                ).trim()}"""
                        }
                    
                    steps {
                        script {
                            env.TF_VAR_available_port = "${TF_VAR_available_port}"
                        }
                        sh '''
                            env 
                            terraform init &&\
                            terraform plan
                            '''
                        }
                    }
                stage('Configure AWS Services (terraform apply)') {                    
                    steps {
                        sh '''
                            env 
                            terraform apply --auto-approve
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
                    
                        LISTENER_RULE_ARN = """${sh(
                        returnStdout: true,
                        script: '''
                            terraform output -json lstnr_rule_arn | jq -r '.'
                        '''    
                    ).trim()}"""
                    
                        TARGET_GROUP_ARN = """${sh(
                        returnStdout: true,
                        script: '''
                            terraform output -json target_group_arn | jq -r '.'
                        '''    
                    ).trim()}"""
                    
                    }
                    
                    steps {
                        sh '''
                            env
                            export PATH=~/.local/bin:$PATH
                            pipenv run python3 ./updateitem.py \
                                --region=${REGION} \
                                --table_name=${DDB_TABLE} \
                                --portnum=${TF_VAR_available_port} \
                                --fqdn=${APP_FQDN} \
                                --alb=${PUBLIC_ALB_ARN} \
                                --cert=${INTERNAL_CERT_ARN}  \
                                --target_grp_arn=${TARGET_GROUP_ARN} \
                                --env=${ENVIRONMENT} \
                                --lstnr_rule_arn=${LISTENER_RULE_ARN} \
                                --listener_arn=${PUBLIC_ALB_LISTENER} \
                                --state="in-use"
                            '''
                        }
                    }
                }            
           }
        stage('Remove Objects in AWS') {
            when { expression { params.ACTION == "DECOMMISSION" } }
            stages {        
                stage('Preparation') { // GET THE LOAB BALANCER NAME, PORT and, CERT TO DELETE
                    input { message "Approve to DELETE Pub ELB Objects in AWS" }
                    environment {
                        RAW_DATA = """${sh(
                            returnStdout: true,
                            script: '''
                                export PATH=~/.local/bin:$PATH
                                pipenv run python3 ./get_item.py --region=${REGION} --fqdn=${APP_FQDN}
                            '''    
                                ).trim()}"""
                        }
                    steps {
                        script {
                        def jsonObj = readJSON text: RAW_DATA
                        env.APP_REGION = jsonObj.region
                        env.ELB =  jsonObj.alb
                        env.APP_ENVIRONMENT = jsonObj.environment
                        env.CERT_ARN = jsonObj.cert
                        env.PORT = jsonObj.port
                        env.LISTENER_RULE_ARN = jsonObj.lstnr_rule_arn
                        env.TG_GROUP_ARN = jsonObj.target_grp_arn
                        env.FQDN = jsonObj.fqdn
                        env.DDB_TABLE = jsonObj.table_name
                        env.LISTENER_ARN = jsonObj.listener_arn
                        }
                    }
                } 
                stage('Cleanup AWS Resources') {            
                    steps {
                        sh '''
                            export PATH=~/.local/bin:$PATH
                            pipenv run python3 ./delete_items.py \
                                --region=${APP_REGION} \
                                --table_name=${DDB_TABLE} \
                                --portnum=${PORT} \
                                --fqdn=${FQDN} \
                                --alb=${ELB} \
                                --cert=${CERT_ARN} \
                                --target_grp_arn=${TG_GROUP_ARN} \
                                --env=${APP_ENVIRONMENT} \
                                --lstnr_rule_arn=${LISTENER_RULE_ARN} \
                                --listener_arn=${LISTENER_ARN} \
                                --state="not-in-use"
                        '''
                        }
                    }
                }
            }               
        }
    post {
        cleanup {
            cleanWs(cleanWhenAborted: false)
        }
    }    
}
