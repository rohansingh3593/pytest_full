"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2282668
===================================================================================================
Test Case      : 2282668
Description    : Verify the permission to Publish in DI Policy File for ItronPubSub Agent2
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Ensure the publish permission is available in the agent policy file.

Step 2 - 
The policyfile of the Itron PubSub agent2 should have the following permission in <Permissions> tag
:<Permission name=\"Data:Publish\"/>


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_agent_and_activate ,ITRONPUBSUBAGENT2
# AUTOGENERATED Test Case 2282668

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2063316")
@pytest.mark.test_case("2282668")
@pytest.mark.parametrize("agent_info", [ITRONPUBSUBAGENT2])
def test_case(preinstalled_meter, logger, di_version,agent_info):
    logger.trace("Executing Test Case 2282668 - Verify the permission to Publish in DI Policy File for ItronPubSub Agent2")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    agentregistrations=preinstalled_meter.sql_query("select AgentName from agentinformation;")
    assert 'ItronPubSubAgent2' in agentregistrations 
    dipolicy_file=preinstalled_meter.sql_query("select PolicyFile from DIPolicyFile where agentid = 50528120")
    logger.trace('Step 2')
    count=0
    for i in dipolicy_file :
        if '<Permission name="Data:Publish"/>' in i :
            count=count+1
    assert count!=0,'PubSub  Agent2 have not permission'



