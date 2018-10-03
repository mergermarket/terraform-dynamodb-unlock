# Terraform Dynamodb Unlock

Remove a lock on a state file

You'll see an error similiar to the following:
```
Error: Error locking state: Error acquiring the state lock: ConditionalCheckFailedException: The conditional request failed
	status code: 400, request id: EHMNPGITLDL8TCJ40GKKLNS64RVV4KQNSO5AEMVJF66Q9ASUAAJG
Lock Info:
  ID:        77b2f12e-7a06-7448-b206-8538cda19710
  Path:      cdflow-tfstate-c3ab7bee01ca/aslive/some-random-service-name/terraform.tfstate
  Operation: OperationTypeApply
  Who:       @2141b9e3c6b2
  Version:   0.11.7
  Created:   2018-01-01 10:21:05.068032938 +0000 UTC
  Info:  
```

You can take the ID from the output and pass it to this docker container.

## Usage

    docker pull mergermarket/terraform-dynamodb-unlock
    docker run -i \
        -e $AWS_ACCESS_KEY_ID -e $AWS_SECRET_ACCESS_KEY \
        mergermarket/terraform-dynamodb-unlock \
            --account myaccount \
            --role admin \
            --region eu-west-1 \
            --role-session-name "$JOB_NAME" \
            --service some-random-service-name \
            --lock-id 77b2f12e-7a06-7448-b206-8538cda19710

## Options

* `--account` - name of the account in organisations for role to assume (required).
* `--role` - name of the role to assume (required).
* `--role-session-name` - session name for the role, so it's easy to identify who did this (required, unless called from an assumed role already).
* `--region` - region where the service is running (required unless `AWS_DEFAULT_REGION` is passed).
* `--service` - name of the service to which has the lock.
* `--lock-id` - ID of the lock to be removed. (required).
