
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379761
===================================================================================================
Test Case      : 2379761
Description    : Meter Reboot : Ensure AppServices version and lxc process ID 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Have the meter with latest AppServ and note the PID of LXC

Step 2 - 


Step 3 - 
Reboot the meter, and Ensure if the AppServ version is retained, lxc PID is updated.

Step 4 - 
Meter should come UP ; lxc should have new PID


===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,is_process_running,wait_for_agents,refresh_container,filter_ps,Active_Containers

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.suite_id("2379530")
@pytest.mark.test_case("2379761")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2379761 - Meter Reboot : Ensure AppServices version and lxc process ID ")
    logger.trace('Step 1')
    
    agent=DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)
    logger.trace('Step 2')
    lxc_container_id_before = sorted(filter_ps(preinstalled_meter,"lxc-start"))
    logger.info(lxc_container_id_before)
    logger.trace('Step 3')
    preinstalled_meter.reboot_meter()
    wait_for_agents(preinstalled_meter,logger,[agent],20*60)
    assert is_process_running(preinstalled_meter,f'{agent.name}_Daemon'),"Agent not properly Functinoal"
    logger.trace('Step 4')
    lxc_container_id_after = sorted(filter_ps(preinstalled_meter,"lxc-start"))
    assert lxc_container_id_after !=lxc_container_id_before








