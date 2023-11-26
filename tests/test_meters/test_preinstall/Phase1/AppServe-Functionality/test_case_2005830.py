"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2005830
===================================================================================================
Test Case      : 2005830
Description    : Verify Installing Third party Agent
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Follow the previous testcase id : 2005826 for the package
ThirdPartyPubSubAgent_0.4.24.377216952_TS.zip

Step 2 - 


Step 3 - 



===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import wait_until_agent_up,Third_Party_PubSub_AGENT,install_agent,filter_ps
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2005830")
@pytest.mark.parametrize("agent_info", [Third_Party_PubSub_AGENT])
def test_case(preinstalled_meter, logger, agent_info):
    logger.trace("Executing Test Case 2005830 - Verify Installing Third party Agent")   
    logger.trace('Step 1')
    install_agent(preinstalled_meter, logger, agent_info)
    cmd='ps | grep Agent'
    wait_until_agent_up_data=wait_until_agent_up(preinstalled_meter,agent_info,cmd)
    assert wait_until_agent_up_data !=0
    ret = filter_ps(preinstalled_meter,"DataServer_Daemon")
    assert 'DataServer_Daemon' in ret[0][4]
    logger.trace('Step 2')
    agent_data=preinstalled_meter.sql_query('select AgentName from agentinformation;')
    assert 'ThirdPartyPubSubAgent' in agent_data
    
   

