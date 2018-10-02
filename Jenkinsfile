pipeline {
  agent none
  options {
    timestamps()
  }
  parameters {
    string(
      name: 'Account',
      defaultValue: '',
      description: 'Name of the account in organisations for role to assume'
    )
    string(
      name: 'Service',
      defaultValue: '',
      description: 'Name of the service which has the lock'
    )
    string(
      name: 'LockID',
      defaultValue: '',
      description: 'ID of the lock to be removed.'
    )
    string(
      name: 'Role',
      defaultValue: 'admin',
      description: 'Name of the role to assume'
    )
    string(
      name: 'Region',
      defaultValue: 'eu-west-1',
      description: 'Region where the service is running'
    )
  }
  stages {
    stage('Delete Terraform lock') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'aws-credentials', passwordVariable: 'AWS_SECRET_ACCESS_KEY', usernameVariable: 'AWS_ACCESS_KEY_ID')]) { 
        sh '''
          docker pull mergermarket/terraform-dynamodb-unlock"
          docker run -i \
              -e $AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_SESSION_TOKEN \
              mergermarket/terraform-dynamodb-unlock \
                --account ${params.Account} \
                --role ${params.Role} \
                --region ${params.Region} \
                --role-session-name "$JOB_NAME" \
                --service ${params.Service} \
                --lock-id ${params.LockID}
          '''
        }               
      }
    }
  }
}