"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993231
===================================================================================================
Test Case      : 1993231
Description    : TmpContainerDir
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify the existence of the /tmp/container directory

Step 2 - 
/tmp/container should be seen when the containers are running.


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import Third_Party_PubSub_AGENT,install_agent_and_activate,Active_Containers
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
 
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993231")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993231 - TmpContainerDir")
    logger.trace('Step 1')
    agent = Third_Party_PubSub_AGENT
    install_agent_and_activate(preinstalled_meter, logger, agent)

    stop = time.time() + 5*60
    while time.time()<=stop:
        Agent_reg_list=preinstalled_meter.sql_query('select Name from agentregistration')
        if Agent_reg_list :logger.info("Available agent name is %s",", ".join(Agent_reg_list))
        if agent.name in Agent_reg_list:
            break
        time.sleep(10)
    assert agent.name in Agent_reg_list, f"{agent.name} is not registered in the AgentRegistration table."

    stop = time.time() + 5*60
    while time.time()<=stop:
        Agent_reg_list=preinstalled_meter.sql_query('select Name from agentregistration')
        status = agent.container_id in Active_Containers(preinstalled_meter)
        if status:
            break
        time.sleep(10)
    assert status, f"{agent.container_id} is not wake up start"

    logger.trace('Step 2')
    dir = preinstalled_meter.ls('/tmp/container')
    assert agent.container_id in dir
