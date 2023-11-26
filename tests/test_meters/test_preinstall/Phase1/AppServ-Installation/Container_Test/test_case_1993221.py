
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993221
===================================================================================================
Test Case      : 1993221
Description    : CMLxcls
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
When the container is running issue the command lxc-ls -P /tmp/container --active

Step 2 - 
lxc-ls --active command should list the running containers


===================================================================================================


"""
import pytest
from tests.test_meters.utils import install_multiple_agents_and_activate,is_process_running,HAN_AGENT,Third_Party_PubSub_AGENT

# AUTOGENERATED Test Case 1993221

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993221")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993221 - CMLxcls")

    logger.trace('Step 1')
    agent_list=[HAN_AGENT,Third_Party_PubSub_AGENT]
    install_multiple_agents_and_activate(preinstalled_meter, logger, agent_list)
    assert is_process_running(preinstalled_meter,"lxc-start")," Container is not running"
    logger.trace('Step 2')
    containers = preinstalled_meter.command('lxc-ls -P /tmp/container --active')
    con_list = ['50593792','587464704']
    for i in containers:
        assert i.strip() in con_list



