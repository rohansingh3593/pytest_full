
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2003736
===================================================================================================
Test Case      : 2003736
Description    : Verify that Container Manager does provide a D-bus Interface to returns list of LXC Container IDs and specific Dbus service path after LXC Container is started
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
Verify the list of containers in a meter with the below command:  dbus-send --system
--dest=com.itron.museplatform.ContainerManager --print-reply --type=method_call
/com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.GetContainerList

Step 2 -
ContainerManager should provide the interface to return List of all active LXC Container IDs and LXC
Container specific Dbus service paths.               # dbus-send --system
--dest=com.itron.museplatform.ContainerManager --print-reply --type=method_call
/com/itron/museplatform/ContainerManager
com.itron.museplatform.Contai\nnerManager.GetContainerList\nmethod return time=1655964388.166737
sender=:1.21 -> destination=:1.31 serial=9 reply_serial=2\n   int32 0\n   array [\n      struct {\n
uint32 50593792\n         string \"unix:path=/tmp/container/50593792/container_bus_socket\"\n
}\n      struct {\n         uint32 587464704\n         string
\"unix:path=/tmp/container/587464704/container_bus_socket\"\n      }\n   ]\n


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import HAN_AGENT,Third_Party_PubSub_AGENT,install_multiple_agents_and_activate

# AUTOGENERATED Test Case 2003736

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2002265")
@pytest.mark.test_case("2003736")
def test_case(preinstalled_meter, logger):
    agent_list = [HAN_AGENT,Third_Party_PubSub_AGENT]
    install_multiple_agents_and_activate(preinstalled_meter, logger, agent_list)
    logger.trace("Executing Test Case 2003736 - Verify that Container Manager does provide a D-bus Interface to returns list of LXC Container IDs and specific Dbus service path after LXC Container is started")

    logger.trace('Step 1')
    containers = ['587464704','50593792']
    timeout = 90
    end = time.time() + timeout
    found = False
    while time.time() < end and not found:
        Container_list=preinstalled_meter.command('dbus-send --system --dest=com.itron.museplatform.ContainerManager --print-reply --type=method_call /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.GetContainerList')
        logger.trace(Container_list)
        data = ''.join(Container_list)
        logger.trace(data)
        found = all([con in data for con in containers])
        if not found:
            logger.info("Waiting for containers")
            time.sleep(10)

    logger.info("Waited %s seconds", time.time() - (end - timeout))

    assert found

    logger.trace('Step 2')
    for con in containers:
        assert con in data, "LXC Container IDs not return"
        assert f"/tmp/container/{con}/container_bus_socket" in data,"specific Dbus service path after LXC Container is started is not return"
