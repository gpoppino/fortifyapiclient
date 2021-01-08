#!/usr/bin/python3

import sys
import os
from os import environ
from dotenv import load_dotenv
from fortifyapi.fortify import FortifyApi

__version__ = "1.0"

# Set encoding
environ["PYTHONIOENCODING"] = "utf-8"

# Set var for connection
description = 'fortifyapi artifact approval client'

def token():
     api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), username=os.getenv('FORTIFY_SSC_USERNAME'), password=os.getenv('FORTIFY_SSC_PASSWORD'), verify_ssl=False)
     response = api.get_token(description=description)
     return response.data['data']['token']

def api():
    api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), token=token(), verify_ssl=False)
    return api

def approve_artifact(artifactId):
    data = { "artifactIds": [ artifactId ], "comment": "fortifyAPIclient CI approval client" }
    url = '/api/v1/artifacts/action/approve'
    return api()._request('POST', url, json=data)

def get_project_version_newest_artifact(projectId):
    url = "/api/v1/projectVersions/" + str(projectId) + "/artifacts?start=-1&limit=1"
    return api()._request('GET', url)

def main(project_name, project_version):
    _api = api()

    response = _api.get_version(project_version)
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
    sys.exit(retcode)
