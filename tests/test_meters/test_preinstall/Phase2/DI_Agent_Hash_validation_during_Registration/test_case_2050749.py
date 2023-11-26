"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050749
===================================================================================================
Test Case      : 2050749
Description    : Verify ApplicationServices compares the two SHA256 has values and matches the hash values with correct DI Policy File hash value
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install any Agent Package. example : DITestAgent
Step 2 - 
Agent successfully installed.
Step 3 - 
Get the  hash value of agent by running the below command :# sha256sum
/tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon
Step 4 - 
# sha256sum /tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon\n489c6f378cc42512ff51
dabdb3a8c1bb1ddf9c1b1edf58d9625f2882cdf12950
/tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon\n
Step 5 - 
Get the hash value from DI policy file
Step 6 - 
<Agent ID=\"50528128\" Name=\"DITestAgent\" Version=\"0.4.23.2914239114\" Priority=\"1\"
Hash=\"489c6f378cc42512ff51dabdb3a8c1bb1ddf9c1b1edf58d9625f2882cdf12950\">
Step 7 - 
Verify Application Services compares two hash value and it matches by comparing manually the two
hash values from Agent API and DI Policy file
Step 8 - 
hash value should match with DI policy file installed
===================================================================================================
"""
import pytest
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT
from tests.test_meters.rohan_utils import absolute_command

# AUTOGENERATED Test Case 2050749
#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050697")
@pytest.mark.test_case("2050749")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(preinstalled_meter, logger, agent_info):
    logger.trace("Executing Test Case 2050749 - Verify ApplicationServices compares the two SHA256 has values and matches the hash values with correct DI Policy File hash value")
    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter, logger, DI_TEST_AGENT)
    logger.trace('Step 2')
    logger.trace('Step 3')
    cmd = 'sha256sum /tmp/container/50593792/rootfs/usr/bin/0302ff80/DITestAgent_Daemon'
    Hash_Value1=absolute_command(preinstalled_meter,cmd)
    logger.trace('Step 4')
    Hash_Value1=Hash_Value1[0].split()[0]
    logger.trace('Step 5')
    query = f"select AgentUID from agentinformation where AgentName = \"{agent_info.name}\""
    agent_id = preinstalled_meter.sql_query(query)[0]
    
    logger.trace('Step 6')
    query = f"select PolicyFile from DIPolicyFile where AgentId = {agent_id}"
    policy_file_content = " ".join(preinstalled_meter.sql_query(query))


    logger.trace('Step 7')
    logger.trace('Step 8')
    assert Hash_Value1 in policy_file_content