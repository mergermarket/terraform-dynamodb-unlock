import argparse
import sys
import re
import boto3

TERRAFORM_LOCKS_TABLE_NAME = 'terraform_locks'

parser = argparse.ArgumentParser(description='Unlock a terraform state lock')
parser.add_argument(
    '--account', required=True, help='The account to assume the role in'
)
parser.add_argument(
    '--role', default='admin', help='The role to assume in the account'
)
parser.add_argument(
    '--role-session-name', default=None,
    help='An identifier for you, to make it easy to see who did this'
)
parser.add_argument('--region', help='The region the service is in')
parser.add_argument('--service', required=True, help='The ECS service')
parser.add_argument(
    '--lock-id', required=True, help='The ID of the lock to be removed'
)
parser.add_argument('--team', help='The ID of the lock to be removed')
args = parser.parse_args()

session = boto3.Session()

orgs = session.client('organizations')

try:
    accounts = {
        account['Name']: account['Id']
        for page in orgs.get_paginator('list_accounts').paginate()
        for account in page['Accounts']
    }
except Exception as e:
    print(str(e), file=sys.stderr)
    sys.exit(1)
account_id = accounts.get(args.account)
if account_id is None:
    print(f'unknown account {args.account}', file=sys.stderr)
    sys.exit(1)
role_arn = f'arn:aws:iam::{account_id}:role/{args.role}'

sts = boto3.client('sts')

if args.role_session_name is not None:
    role_session_name = re.sub(r'[^\w=,.@-]', '-', args.role_session_name)[:64]
else:
    caller_identity = sts.get_caller_identity()
    match = re.search(r':assumed-role/[^/]+/([^/]+)$', caller_identity['Arn'])
    if match is None:
        print(
            f'--role-session-name is required for IAM user credentials',
            file=sys.stderr
        )
        sys.exit(1)
    role_session_name = match.group(1)

try:
    credentials = sts.assume_role(
        RoleArn=role_arn,
        RoleSessionName=role_session_name
    )['Credentials']
except Exception as e:
    print(f'could not assume role {role_arn}:\n\n{e}', file=sys.stderr)
    sys.exit(1)

print(f'assumed role {role_arn}', file=sys.stderr)

dynamodb = boto3.client(
    'dynamodb',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name=args.region
)

if (args.account == "acurisrelease" and args.team is not None) and \
    (args.account == "acurisrelease" and args.team is not ""):
    TERRAFORM_LOCKS_TABLE_NAME = args.team + "-tflocks"


print(f'Identifying lock for {args.service}...', file=sys.stderr)
lock_key_items = dynamodb.scan(
    ExpressionAttributeNames={
        '#lock': 'LockID',
    },
    ExpressionAttributeValues={
        ':lock_id': {
            'S': args.lock_id
        },
        ':service_name': {
            'S': args.service
        }
    },
    FilterExpression=(
        'contains(LockID, :service_name) AND contains(Info, :lock_id)'
    ),
    ProjectionExpression='#lock',
    TableName=TERRAFORM_LOCKS_TABLE_NAME,
)['Items']

if len(lock_key_items) != 1:
    print('A single lock ID could not be found.', file=sys.stderr)
    sys.exit(1)

lock_key = lock_key_items[0]['LockID']['S']
print(f'Deleting lock with lock ID {lock_key}...', file=sys.stderr)

dynamodb.delete_item(
    TableName=TERRAFORM_LOCKS_TABLE_NAME,
    Key={
        'LockID': {
            'S': lock_key
        }
    },
    ReturnValues='ALL_OLD'
)
print('Lock Deleted.', file=sys.stderr)
