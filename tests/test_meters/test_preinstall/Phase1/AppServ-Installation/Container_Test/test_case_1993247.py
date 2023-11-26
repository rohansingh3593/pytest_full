"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993247
===================================================================================================
Test Case      : 1993247
Description    : Verify watchdog gets triggered from init and sends events to CMD. 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check for the active containers :# lxc-ls -P /tmp/container --active\n

Step 2 - 
===================================================================================================

"""
import pytest
from tests.test_meters.utils import Third_Party_PubSub_AGENT,install_agent_and_activate
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993247")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993247 - Verify watchdog gets triggered from init and sends events to CMD. ")
    agent = Third_Party_PubSub_AGENT
    install_agent_and_activate(preinstalled_meter, logger, Third_Party_PubSub_AGENT)
    logger.trace('Step 1')
    container_data=preinstalled_meter.command('lxc-ls -P /tmp/container --active')
    container_data = " ".join(container_data)
    assert Third_Party_PubSub_AGENT.container_id in container_data
    


