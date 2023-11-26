
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2380400
===================================================================================================
Test Case      : 2380400
Description    : Refresh the container and ensure if the Container PID
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Stop and refresh the container using DBUS command \ndbus-send\n--type=signal  -system  -dest=com.itr
on.museplatform.ContainerManager/com/itron/museplatform/ContainerManager\ncom.itron.museplatform.Con
tainerManager.StopAllContainer -- All the running\ncontainers should be stopped with Dbus
StopAllContainer signal dbus-send\n--type=signal --system --dest=com.itron.museplatform.ContainerMan
ager/com/itron/museplatform/ContainerManagercom.itron.museplatform.ContainerManager.Refresh --
Refresh all the containers\n

Step 2 - 
New PID should be available


===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,refresh_container,Active_Containers,filter_ps
from tests.test_meters.rohan_utils import agent_file,Container_stop

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379530")
@pytest.mark.test_case("2380400")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2380400 - Refresh the container and ensure if the Container PID")
    logger.trace('Step 1')
    
    agent = DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)
    lxc_container_id_before = sorted(filter_ps(preinstalled_meter,"lxc-start"))
    logger.info(lxc_container_id_before)
    # Stop the Container
    Container_stop(preinstalled_meter,agent.container_id)
    # Start the container
    refresh_container(preinstalled_meter,logger,20*60)
    assert agent.container_id in Active_Containers(preinstalled_meter),f"Container {agent.container_id} is not start after the Container Start command"
    logger.trace('Step 2')
    lxc_container_id_after = sorted(filter_ps(preinstalled_meter,"lxc-start"))
    assert lxc_container_id_after !=lxc_container_id_before


   