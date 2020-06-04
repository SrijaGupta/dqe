def groups = ""
def DEVICE_GROUP_NAME = ""
pipeline {
    agent any
    // options {
    //     skipDefaultCheckout true
    // }
    parameters{
        string(name:'COMMIT_DEVICE_INV_HOSTNAMES',description:'Enter COMMIT_DEVICE_INV_HOSTNAMES name')
        string(name:'groups',description:'Enter device group name')
    }
        environment {
        ANSIBLE_BASE="./ansible"
        JSNAPY_BASE="./jsnapy"
        INVENTORY_FILE_PATH="${WORKSPACE}/${ANSIBLE_BASE}/ansible/inventory/cluster_inventory.inv"
        CONFIG_FRAGMENT_TEMPLATE_REPO_DIR="${WORKSPACE}"
        CONFIG_FRAGMENT_TEMPLATE_BASE_DIR="${CONFIG_FRAGMENT_TEMPLATE_REPO_DIR}/ansible/${ANSIBLE_BASE}/templates"
        ANSIBLE_HOST_KEY_CHECKING="False"
        JSNAPY_TESTFILE_DIR="${WORKSPACE}/${JSNAPY_BASE}/testfiles"
        JSNAPY_OUTPUT_DIR="${DQNET_DEVICE_DATA_DIR}/jsnapy"
        COMMIT_DEVICE_INV_HOSTNAMES="${COMMIT_DEVICE_INV_HOSTNAMES}"
        NETDEV_DEVICE_IP_LIST="10.102.164.36 10.102.164.240 10.102.164.238 10.102.164.233 10.102.164.230 10.102.164.22 10.102.164.218"
        NETDEV_DEVICE_LOGIN_USERNAME="northstar"
        NETDEV_DEVICE_CLI_USERNAME="northstar"
        NETDEV_DEVICE_CLI_PASSWORD="Embe1mpls"
        NETDEV_FABRIC_NAME="Fab1"
        ANSIBLE_CONFIG="/etc/ansible/ansible.cfg"
        DEVICE_GROUP_NAME="${params.groups}.split()"
        DQNET_DEVICE_DATA_DIR="${WORKSPACE}/ansible/"
        
       
    }

    stages {
        stage('Playbooks'){
            steps{
                echo 'Cloning Ansible Playbooks...'
                sh "python --version"
                sh "python3 --version"
                sh "ansible --version"
                dir ("${ANSIBLE_BASE}") {
                    sh 'pwd'
                    sh 'rm -rf ./ansible/roles/Juniper.junos/.gitkeep'
                    checkout([$class: 'GitSCM', branches: [[name: 'master']], doGenerateSubmoduleConfigurations: false, extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'pat-dqe', url: 'https://css-git.juniper.net/srigupta/dqe-workflow-automation.git']]])
                    echo 'prev2'            
                    
                }
                sh "ls -lart ./; cd ${ANSIBLE_BASE}; ls -lart"
            }
        }
        stage('Keys Upload'){
            steps{
                sh "cd ${ANSIBLE_BASE}/ansible;./run_netdev_junos_device_upload_authorized_keys.sh"
                sh "cd ${ANSIBLE_BASE}/ansible;./run_netdev_junos_inventory_gen.sh"
                sh " touch ${WORKSPACE}/ansible/result.txt"
            }
        }
        stage('Groups') {
            steps {
                script {
                    def stepsForParallel = [:]
                    def branches = [:]
                    //groups = sh(returnStdout: true, script: 'echo ACX2200 MX10442 cluster_fabric_mx_devices')
                    //branches = groups.split()
                    branches = "${params.groups}".split()
                    branches.each {
                        def stepName = "${it}"
                        stepsForParallel[stepName] = { ->           
                            sh "echo ansible-playbook -i host ${it}"
                            sh "export DEVICE_GROUP_NAME=${it}; cd ${ANSIBLE_BASE}/ansible; ./run_netdev_junos_config_gen_commitcheck.sh"
                            sh "export DEVICE_GROUP_NAME=${it}; cd ${ANSIBLE_BASE}/ansible; ./run_netdev_junos_config_diff_report.sh"
                            sh "export DEVICE_GROUP_NAME=${it}; cd ${ANSIBLE_BASE}/ansible; ./run_netdev_junos_config_gen_commit.sh ${COMMIT_DEVICE_INV_HOSTNAMES}"
                            sh "echo srija-test4 artifact"
                            sh "cat ${WORKSPACE}/ansible/junos_config_diff/${it}/${it}_config_diff_report.yml >> ${WORKSPACE}/ansible/result.txt"
                            sh "pwd"
                            archiveArtifacts '**/result.txt'
                        }
                        
                    }
                    parallel stepsForParallel
                }
            }
        

            }
        }
}
