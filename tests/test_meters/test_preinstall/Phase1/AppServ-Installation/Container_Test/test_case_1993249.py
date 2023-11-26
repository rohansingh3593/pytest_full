#ready to pr
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993249
===================================================================================================
Test Case      : 1993249
Description    : Verify resources are released back to the host once the Container is stopped
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Verify that the resources such as CPU/Memory are released back to the host system
Check the resources details when the containers are running.
# df /tmp/container
Step 2 -
When the containers are stopped , All the occupied resources should get released to the host system
Stop the container :
dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer
Verify that the resources such as CPU/Memory are released back to the host system
When the containers are stopped , All the occupied resources should get released to the host system
df /tmp/container

===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import DI_TEST_AGENT, install_multiple_agents_and_activate,V7_AGENT, refresh_container,install_agent_and_activate,Active_Containers


#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993249")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993249 - Verify resources are released back to the host once the Container is stopped ")
    logger.trace('Step 1')
    agent = DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)
    container = preinstalled_meter.ls("/tmp/container")
    assert agent.container_id in container
    cpu_use = preinstalled_meter.command("df /tmp/container")
    cpu_used_before_stop = cpu_use[1].split()
    logger.trace("Before: %s", cpu_used_before_stop)
    logger.trace('Step 2')
    try:
        preinstalled_meter.command('dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer')

        stop = time.time() + (5*60)
        while time.time()<=stop:
            output= not Active_Containers(preinstalled_meter)
            if output:
                break
            time.sleep(10)
        assert output , 'Container is still running'

        # # It will check the occupied resources to the host system.
        stop=time.time() + 5*60
        while stop>time.time():
            cpu_use = preinstalled_meter.command("df /tmp/container")
            cpu_used_after_stop = cpu_use[1].split()
            logger.trace("After: %s", cpu_used_after_stop)
            #Memory Used
            value1 =  int(cpu_used_before_stop[2]) >= int(cpu_used_after_stop[2])
            #Memory Available
            value2 =   int(cpu_used_before_stop[3]) <= int(cpu_used_after_stop[3])
            #Memory Used %
            value3 =   int(cpu_used_before_stop[4].replace('%','')) >= int(cpu_used_after_stop[4].replace('%',''))
            status = value1 and value2 and value3
            if status:
                break
            time.sleep(5)

        assert status ,f"All the occupied resources is not released to the host system"

    finally:
        refresh_container(preinstalled_meter, logger,20*60)