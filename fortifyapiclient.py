#!/usr/bin/python3

import sys, os, requests, base64
from os import environ
from dotenv import load_dotenv
from fortifyapi.fortify import FortifyApi

__version__ = "1.1"

# Set encoding
environ["PYTHONIOENCODING"] = "utf-8"

# Set var for connection
description = 'fortifyapi artifact approval client'

my_basic_auth_headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json;charset=UTF-8',
    'User-Agent': 'fortifyapiclient ' + __version__
}

_api = None

def token():
    api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), username=os.getenv('FORTIFY_SSC_USERNAME'), password=os.getenv('FORTIFY_SSC_PASSWORD'), verify_ssl=False)
    response = api.get_token(description=description)
    return response.data['data']['token']

def api():
    global _api
    if _api != None:
        return _api
    _api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), token=token(), verify_ssl=False)
    return _api

def basic_auth_request(method, url, json=None):
    auth = os.getenv('FORTIFY_SSC_USERNAME') + ":" + os.getenv('FORTIFY_SSC_PASSWORD')
    my_basic_auth_headers['Authorization'] = "Basic %s" % base64.b64encode(auth.encode("utf-8")).decode()
    return requests.request(method, os.getenv('FORTIFY_SSC_URL') + url, json=json, headers=my_basic_auth_headers)

def cleanup():
    data = {
        'tokens': [ api().token ]
    }
    url = '/api/v1/tokens/action/revoke'
    global _api
    _api = None
    return basic_auth_request('POST', url, data)

def approve_artifact(artifactId):
    data = { "artifactIds": [ artifactId ], "comment": "fortifyAPIclient CI approval client" }
    url = '/api/v1/artifacts/action/approve'
    return api()._request('POST', url, json=data)

def get_project_version_newest_artifact(projectId):
    url = "/api/v1/projectVersions/" + str(projectId) + "/artifacts?start=-1&limit=1"
    return api()._request('GET', url)

def main(project_name, project_version):
    response = api().get_version(project_version)
    artifacts_found = None
    for project in response.data['data']:
        if project['project']['name'] == project_name:
            response = get_project_version_newest_artifact(project['id'])
            if response != None:
                artifacts_found = response.data['data']
            break

    if artifacts_found == None:
        print("No artifacts found for app version: {0} {1}".format(project_name, project_version))
        return 1

    for artifact in artifacts_found:
        if artifact['status'] == "REQUIRE_AUTH":
                print("Approving artifact Id: {0}".format(artifact['id']))
                response = approve_artifact(artifact['id'])
                if response.response_code == 200:
                    print("Artifact Id approved: {0}".format(artifact['id']))
                    break
                else:
                    print(response)
                    return 1
        else:
            print("No artifacts to approve found for app version: {0} {1}".format(project_name, project_version))
            return 1

    return 0

if __name__ == '__main__':
    load_dotenv()
    retcode = main(sys.argv[1], sys.argv[2])
    print("Token clean up response code: {0}".format(cleanup().status_code))
    sys.exit(retcode)
