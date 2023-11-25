#!/usr/bin/env python3

import os

print("WARNING: this script is deprecated.  use pytest-ads-testplan pytest plugin instead")

from azure.devops.connection import Connection
from msrest.authentication import BasicAuthentication
import json

def main(output):
    # Fill in with your personal access token and org URL
    personal_access_token = os.getenv('SYSTEM_ACCESSTOKEN')
    organization_url = 'https://dev.azure.com/Crosslynxusllc'
    # Create a connection to the org
    credentials = BasicAuthentication('', personal_access_token)
    connection = Connection(base_url=organization_url, creds=credentials)

    # Get a client (the "core" client provides access to projects, teams, etc)
    core_client = connection.clients.get_core_client()

    project = 'VGS_Automation_and_COE_Testing'

    build_client = connection.clients.get_build_client()

    bld_id = os.getenv("DOWNLOADPIPELINEARTIFACT_BUILDNUMBER")
    pipeline_build_id = os.getenv("BUILD_BUILDNUMBER")

    build_number="private build"
    if bld_id:
        build = build_client.get_build(project, bld_id)
        print("Build Artifact: ", build)
        build_dict = {}
        for key, item in vars(build).items():
            if isinstance(item, object) and hasattr(item, '__dict__'):
                build_dict[key] = {key:str(i) for key,i in vars(item).items()}
            elif type(item) is dict:
                build_dict[key] = item
            else:
                build_dict[key] = str(item)

        print("Dict: ", build_dict)
        #Build Artifact:  {'additional_properties': {'appendCommitMessageToRunName': True}, '_links': <azure.devops.v5_1.build.models.ReferenceLinks object at 0x7f1edff1d490>, 'agent_specification': None, 'build_number': 'NB_DIAppServices_20221012001_master', 'build_number_revision': 1, 'controller': None, 'definition': <azure.devops.v5_1.build.models.DefinitionReference object at 0x7f1ee00f1160>, 'deleted': None, 'deleted_by': None, 'deleted_date': None, 'deleted_reason': None, 'demands': None, 'finish_time': datetime.datetime(2022, 10, 12, 8, 9, 1, 189452, tzinfo=<isodate.tzinfo.Utc object at 0x7f1ee0934c70>), 'id': 1401794, 'keep_forever': True, 'last_changed_by': <azure.devops.v5_1.build.models.IdentityRef object at 0x7f1ee00f11f0>, 'last_changed_date': datetime.datetime(2022, 10, 12, 8, 9, 2, 280000, tzinfo=<isodate.tzinfo.Utc object at 0x7f1ee0934c70>), 'logs': <azure.devops.v5_1.build.models.BuildLogReference object at 0x7f1ee00f1220>, 'orchestration_plan': <azure.devops.v5_1.build.models.TaskOrchestrationPlanReference object at 0x7f1ee00f1340>, 'parameters': None, 'plans': [<azure.devops.v5_1.build.models.TaskOrchestrationPlanReference object at 0x7f1ee00f1100>], 'priority': 'normal', 'project': <azure.devops.v5_1.build.models.TeamProjectReference object at 0x7f1ee00f10a0>, 'properties': {}, 'quality': None, 'queue': <azure.devops.v5_1.build.models.AgentPoolQueue object at 0x7f1ee00f1370>, 'queue_options': None, 'queue_position': None, 'queue_time': datetime.datetime(2022, 10, 12, 8, 0, 23, 177161, tzinfo=<isodate.tzinfo.Utc object at 0x7f1ee0934c70>), 'reason': 'schedule', 'repository': <azure.devops.v5_1.build.models.BuildRepository object at 0x7f1ee011d2e0>, 'requested_by': <azure.devops.v5_1.build.models.IdentityRef object at 0x7f1ee011de80>, 'requested_for': <azure.devops.v5_1.build.models.IdentityRef object at 0x7f1ee011de20>, 'result': 'succeeded', 'retained_by_release': False, 'source_branch': 'refs/heads/master', 'source_version': 'ba9c8ae090cd3ef8fb775c87371aeb8155200024', 'start_time': datetime.datetime(2022, 10, 12, 8, 0, 32, 910650, tzinfo=<isodate.tzinfo.Utc object at 0x7f1ee0934c70>), 'status': 'completed', 'tags': [], 'triggered_by_build': None, 'trigger_info': {'scheduleName': None}, 'uri': 'vstfs:///Build/Build/1401794', 'url': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/Builds/1401794', 'validation_results': []}
        #Dict:  {'additional_properties': "{'appendCommitMessageToRunName': True}", '_links': "{'additional_properties': {'web': {'href': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_build/results?buildId=1401794'}, 'badge': {'href': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/status/3649'}, 'self': {'href': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/Builds/1401794'}, 'sourceVersionDisplayUri': {'href': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/builds/1401794/sources'}, 'timeline': {'href': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/builds/1401794/Timeline'}}, 'links': None}", 'agent_specification': 'None', 'build_number': 'NB_DIAppServices_20221012001_master', 'build_number_revision': '1', 'controller': 'None', 'definition': "{'additional_properties': {'drafts': []}, 'created_date': None, 'id': 3649, 'name': 'DI.AppServices-Nightly', 'path': '\\\\RivaPlatformASIC\\\\AppServices', 'project': <azure.devops.v5_1.build.models.TeamProjectReference object at 0x7f2faaff89d0>, 'queue_status': 'paused', 'revision': 6, 'type': 'build', 'uri': 'vstfs:///Build/Definition/3649', 'url': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/Definitions/3649?revision=6'}", 'deleted': 'None', 'deleted_by': 'None', 'deleted_date': 'None', 'deleted_reason': 'None', 'demands': 'None', 'finish_time': '2022-10-12 08:09:01.189452+00:00', 'id': '1401794', 'keep_forever': 'True', 'last_changed_by': "{'additional_properties': {}, '_links': <azure.devops.v5_1.build.models.ReferenceLinks object at 0x7f2faafb1130>, 'descriptor': 's2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'display_name': 'Microsoft.VisualStudio.Services.TFS', 'url': 'https://spsprodeus21.vssps.visualstudio.com/A4cba9a70-2854-4868-a594-5ddd2a023909/_apis/Identities/00000002-0000-8888-8000-000000000000', 'directory_alias': None, 'id': '00000002-0000-8888-8000-000000000000', 'image_url': 'https://dev.azure.com/itron/_apis/GraphProfile/MemberAvatars/s2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'inactive': None, 'is_aad_identity': None, 'is_container': None, 'is_deleted_in_origin': None, 'profile_url': None, 'unique_name': '00000002-0000-8888-8000-000000000000@2c895908-04e0-4952-89fd-54b0046d6288'}", 'last_changed_date': '2022-10-12 08:09:02.280000+00:00', 'logs': "{'additional_properties': {}, 'id': 0, 'type': 'Container', 'url': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/builds/1401794/logs'}", 'orchestration_plan': "{'additional_properties': {}, 'orchestration_type': None, 'plan_id': 'c3c9271c-9c8b-4445-9e30-0b4a5ce00cd0'}", 'parameters': 'None', 'plans': '[<azure.devops.v5_1.build.models.TaskOrchestrationPlanReference object at 0x7f2faafb1100>]', 'priority': 'normal', 'project': "{'additional_properties': {}, 'abbreviation': None, 'default_team_image_url': None, 'description': 'Team Project for all things R&D (non-Software)', 'id': '4fc412f1-9337-4c85-8aaf-7955d066a31c', 'last_update_time': datetime.datetime(2022, 10, 10, 16, 18, 19, 450000, tzinfo=<isodate.tzinfo.Utc object at 0x7f2fab7f5c70>), 'name': 'RnD', 'revision': 4491, 'state': 'wellFormed', 'url': 'https://dev.azure.com/itron/_apis/projects/4fc412f1-9337-4c85-8aaf-7955d066a31c', 'visibility': 'private'}", 'properties': '{}', 'quality': 'None', 'queue': "{'additional_properties': {}, '_links': None, 'id': 790, 'name': 'RivaPlatform', 'pool': <azure.devops.v5_1.build.models.TaskAgentPoolReference object at 0x7f2faafb10d0>, 'url': None}", 'queue_options': 'None', 'queue_position': 'None', 'queue_time': '2022-10-12 08:00:23.177161+00:00', 'reason': 'schedule', 'repository': "{'additional_properties': {}, 'checkout_submodules': False, 'clean': None, 'default_branch': None, 'id': '32bcaea8-b4dc-4ee2-b271-923780f97c0f', 'name': 'DI.AppServices', 'properties': None, 'root_folder': None, 'type': 'TfsGit', 'url': 'https://dev.azure.com/itron/RnD/_git/DI.AppServices'}", 'requested_by': "{'additional_properties': {}, '_links': <azure.devops.v5_1.build.models.ReferenceLinks object at 0x7f2faafdee50>, 'descriptor': 's2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'display_name': 'Microsoft.VisualStudio.Services.TFS', 'url': 'https://spsprodeus21.vssps.visualstudio.com/A4cba9a70-2854-4868-a594-5ddd2a023909/_apis/Identities/00000002-0000-8888-8000-000000000000', 'directory_alias': None, 'id': '00000002-0000-8888-8000-000000000000', 'image_url': 'https://dev.azure.com/itron/_apis/GraphProfile/MemberAvatars/s2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'inactive': None, 'is_aad_identity': None, 'is_container': None, 'is_deleted_in_origin': None, 'profile_url': None, 'unique_name': '00000002-0000-8888-8000-000000000000@2c895908-04e0-4952-89fd-54b0046d6288'}", 'requested_for': "{'additional_properties': {}, '_links': <azure.devops.v5_1.build.models.ReferenceLinks object at 0x7f2faafdeee0>, 'descriptor': 's2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'display_name': 'Microsoft.VisualStudio.Services.TFS', 'url': 'https://spsprodeus21.vssps.visualstudio.com/A4cba9a70-2854-4868-a594-5ddd2a023909/_apis/Identities/00000002-0000-8888-8000-000000000000', 'directory_alias': None, 'id': '00000002-0000-8888-8000-000000000000', 'image_url': 'https://dev.azure.com/itron/_apis/GraphProfile/MemberAvatars/s2s.MDAwMDAwMDItMDAwMC04ODg4LTgwMDAtMDAwMDAwMDAwMDAwQDJjODk1OTA4LTA0ZTAtNDk1Mi04OWZkLTU0YjAwNDZkNjI4OA', 'inactive': None, 'is_aad_identity': None, 'is_container': None, 'is_deleted_in_origin': None, 'profile_url': None, 'unique_name': '00000002-0000-8888-8000-000000000000@2c895908-04e0-4952-89fd-54b0046d6288'}", 'result': 'succeeded', 'retained_by_release': 'False', 'source_branch': 'refs/heads/master', 'source_version': 'ba9c8ae090cd3ef8fb775c87371aeb8155200024', 'start_time': '2022-10-12 08:00:32.910650+00:00', 'status': 'completed', 'tags': '[]', 'triggered_by_build': 'None', 'trigger_info': "{'scheduleName': None}", 'uri': 'vstfs:///Build/Build/1401794', 'url': 'https://dev.azure.com/itron/4fc412f1-9337-4c85-8aaf-7955d066a31c/_apis/build/Builds/1401794', 'validation_results': '[]'}
        data = json.dumps(build_dict, indent=4)
        print ("Str: ", data)
        with open(output, "w") as out:
            out.write(data)
    else:
        build = None

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--output', type=str, default="output.yaml", required=True)
args = parser.parse_args()

main(args.output)
