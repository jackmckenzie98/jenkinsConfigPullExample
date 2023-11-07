# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import requests
import json
import os
import boto3

migrate_from = os.environ.get('MIGRATE_FROM')

#Pull secret from secrets manager
def get_secret(secret_name):
    region_name = "us-east-1"
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )
    secret_response = client.get_secret_value(
        SecretId=secret_name
    )
    secrets = json.loads(secret_response['SecretString'])
    return secrets


with open("apiCalls.json") as f:
    endpoint = json.load(f)

session = requests.Session()
SECRETS_FILE = ""
secrets_file_path = os.path.join(os.path.dirname(__file__), SECRETS_FILE)
with open(secrets_file_path) as f:
    secrets = json.load(f)

session.auth = (secrets["username"], secrets["password"])
session.headers.update({'X-XSRF-Header': 'PingFederate'})
session.headers.update({'Accept': '*/*', 'Accept-Encoding': 'gzip, deflate, br'})
session.verify = False
#Create a directory for the artifacts in the current working directory
WORKING_DIRECTORY = os.getcwd()
ARTIFACTS_PATH = os.path.join(WORKING_DIRECTORY, r'artifactsPull')
CERTIFICATES_PATH = os.path.join(ARTIFACTS_PATH, r'certs')
if not os.path.exists(ARTIFACTS_PATH):
    os.makedirs(os.path.join(WORKING_DIRECTORY, r'artifactsPull'))

if not os.path.exists(CERTIFICATES_PATH):
    os.makedirs(os.path.join(ARTIFACTS_PATH, f'certs'))

def make_calls():
    clients = session.get(migrate_from + endpoint["oauthClients"]["endpoint"]).json()
    spConnections = session.get(migrate_from + endpoint["spConnections"]["endpoint"]).json()
    authPolicies = session.get(migrate_from + endpoint["authPolicies"]["endpoint"]).json()
    idpAdapters = session.get(migrate_from + endpoint["idpAdapters"]["endpoint"]).json()
    passwordCVs = session.get(migrate_from + endpoint["passwordCredentialValidators"]["endpoint"]).json()
    accessTokenManagers = session.get(migrate_from + endpoint["accessTokenManagers"]["endpoint"]).json()
    accessTokenMappings = session.get(migrate_from + endpoint["accessTokenMappings"]["endpoint"]).json()
    authPolicyContracts = session.get(migrate_from + endpoint["authPolicyContracts"]["endpoint"]).json()
    authenticationPolicyFragments = session.get(migrate_from +
                                                endpoint["authenticationPolicyFragments"]["endpoint"]).json()
    return [clients, spConnections, authPolicies, authenticationPolicyFragments, idpAdapters, passwordCVs, accessTokenManagers, accessTokenMappings,\
        authPolicyContracts]


#Format any JSON objects that are not formatted in the same way as the others, with a JSON object that wraps it in "items",
#like the other objects do.
def format_object(list_deal):
    for i in range(0, len(list_deal)):
        #Check if the type is a list, because if so it should be wrapped in "items" key
        if type(list_deal[i]) is list:
            list_deal[i] = {
                "items" : list_deal[i]
            }
        #Check if type is a dictionary but does not have "items" key that matches other file formats
        if type(list_deal[i]) is dict:
            if 'items' not in list_deal[i]:
                list_deal[i] = {
                    "items": [list_deal[i]]
                }
    return list_deal

def write_to_file(list_passed):
    file_names = ["clients", "spConnections", "authPolicies", "authenticationPolicyFragments", "idpAdapters",
                  "passwordCredentialValidators", "accessTokenManagers", "accessTokenMappings", "authPolicyContracts"]
    for name, obj in zip(file_names, list_passed):
        f = open(f"{ARTIFACTS_PATH}/{name}.json", 'w+')
        f.write(json.dumps(obj, indent=3))
        f.close()


list_passed = make_calls()
formatted_list = format_object(list_passed)
write_to_file(formatted_list)


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
