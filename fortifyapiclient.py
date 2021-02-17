#!/usr/bin/python3

import sys, os, getopt
from os import environ
from dotenv import load_dotenv
from fortifyapi.fortify import FortifyApi

__version__ = "2.0"

# Set encoding
environ["PYTHONIOENCODING"] = "utf-8"

# Set var for connection
description = 'fortify-api-client'

class FortifyApiClient:

    def __init__(self):
        self.__api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), token=self.__token(), verify_ssl=False)

    def __token(self):
        api = FortifyApi(host=os.getenv('FORTIFY_SSC_URL'), username=os.getenv('FORTIFY_SSC_USERNAME'), password=os.getenv('FORTIFY_SSC_PASSWORD'), verify_ssl=False)
        response = api.get_token(description=description)
        return response.data['data']['token']

    def __approve_artifact(self, artifactId):
        data = { "artifactIds": [ artifactId ], "comment": "fortifyAPIclient CI approval client" }
        url = '/api/v1/artifacts/action/approve'
        return self.__api._request('POST', url, json=data)

    def __get_project_version_newest_artifact(self, projectId):
        url = "/api/v1/projectVersions/" + str(projectId) + "/artifacts?start=-1&limit=1"
        return self.__api._request('GET', url)

    def find_project_version(self, project_name, project_version):
        response = self.__api.get_version(project_version)
        for project in response.data['data']:
            if project['project']['name'] == project_name:
                return project['id']
        return None

    def approve(self, project_name, project_version):
        project_id = self.find_project_version(project_name, project_version)
        artifacts_found = None
        if project_id != None:
            response = self.__get_project_version_newest_artifact(project_id)
            if response != None:
                artifacts_found = response.data['data']

        if artifacts_found == None or artifacts_found == []:
            print("No artifacts found for app version: {0} {1}".format(project_name, project_version))
            return 1

        for artifact in artifacts_found:
            if artifact['status'] == "REQUIRE_AUTH":
                    print("Approving artifact Id: {0}".format(artifact['id']))
                    response = self.__approve_artifact(artifact['id'])
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

    def __create_project(self, project_name, project_version):
        data = {
            "name": project_version,
            "description": "",
            "active": True,
            "committed": False,
            "issueTemplateId": "Prioritized-HighRisk-Project-Template",
            "project": {
                "name": project_name,
                "description": "",
                "createdBy": description,
                "issueTemplateId": "Prioritized-HighRisk-Project-Template",
            }
        }
        url = '/api/v1/projectVersions'
        return self.__api._request('POST', url, json=data)

    def __update_project_attributes(self, id):
        data = [
            {
                "guid":"DevPhase",
                "attributeDefinitionId":"5",
                "values": [{ "guid":"Active" }]
            },
            {
                "guid":"Accessibility",
                "attributeDefinitionId":"7",
                "values": [{ "guid":"externalpublicnetwork" }]
            },
            {
                "guid":"DevStrategy",
                "attributeDefinitionId":"6",
                "values": [{ "guid":"Internal" }]
            }
        ]

        url = '/api/v1/projectVersions/{0}/attributes'.format(id)
        return self.__api._request('PUT', url, json=data)

    def __commit_project(self, project_id):
        data = {
            "committed": True,
            "currentState": {
                "committed": True,
            }
        }
        url = '/api/v1/projectVersions/{0}'.format(project_id)
        return self.__api._request('PUT', url, json=data)

    def create(self, project_name, project_version):
        project = self.find_project_version(project_name, project_version)
        if project != None:
            print("Project already exists with ID: " + str(project))
            return 0

        response = self.__create_project(project_name, project_version)
        if response.response_code == 201:
            project_id = response.data['data']['id']
            print("Project created with Id: {0}".format(project_id))
            response = self.__update_project_attributes(project_id)
            if response.response_code == 200:
                self.__commit_project(project_id)
        else:
            print(response)
            return 1

def usage():
    print("Options:")
    print(" -a | --approve [PROJECT_NAME] [VERSION]")
    print(" -c | --create [PROJECT_NAME] [VERSION]")
    print(" -h | --help")

def main(argv):
    try:
        opts, args = getopt.getopt(argv, "ach", ["approve", "create", "help"])
    except getopt.GetoptError as err:
        print(err)
        usage()
        return 2

    if len(args) != 2:
        usage()
        return 2

    fortifyApiClient = FortifyApiClient()
    for opt, arg in opts:
        if opt in ("-a", "--approve"):
            fortifyApiClient.approve(args[0], args[1])
        elif opt in ("-c", "--create"):
            fortifyApiClient.create(args[0], args[1])
        elif opt in ("-h", "--help"):
            usage()
            return 0

if __name__ == '__main__':
    load_dotenv()
    retcode = main(sys.argv[1:])
    sys.exit(retcode)
