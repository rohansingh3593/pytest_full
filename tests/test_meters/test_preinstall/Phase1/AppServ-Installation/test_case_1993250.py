
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993250
===================================================================================================
Test Case      : 1993250
Description    : Perf:Measure the time taken by the container to get started as well as to get stopped
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install Itron PubSub and 3rdParty PubSub Agents.

Step 2 - 
Constainers should be created ps | grep -i lxc

Step 3 - 
Verify that the container takes very little time to get started as well as to get stopped.  #dbus-
send --system--dest=com.itron.museplatform.ContainerManager\n/com/itron/museplatform/ContainerManage
r\ncom.itron.museplatform.ContainerManager.StopAllContainer

Step 4 - 
Should stop both the containers (within 30sec)

Step 5 - 
#dbus-send --type=signal --system --dest=com.itron.museplatform.ContainerManager
/com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh

Step 6 - 
Should start containers (within 35sec)


===================================================================================================


"""

import pytest
from tests.test_meters.utils import install_agent_and_activate,is_process_running,P2P_AGENT,Third_Party_PubSub_AGENT
import time
# AUTOGENERATED Test Case 1993250

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993250")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993250 - Perf:Measure the time taken by the container to get started as well as to get stopped")

    try:

        logger.trace('Step 1')
        agent_list=[Third_Party_PubSub_AGENT,P2P_AGENT]
        for agent in agent_list:
            install_agent_and_activate(preinstalled_meter,logger,agent)

        logger.trace('Step 2')
        assert is_process_running(preinstalled_meter,"lxc"),"Containers is not created"

        logger.trace('Step 3')
        stop_time=time.time()
        preinstalled_meter.command("dbus-send --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.StopAllContainer")
        stop = time.time() + (40)
        while time.time()<=stop:
            """
            Process is running and wait for stop
            """
            if not is_process_running(preinstalled_meter,"lxc-start") :
                break
            time.sleep(3)
        assert not is_process_running(preinstalled_meter,"lxc-start"),"timeout error waiting for conditions"
        stop_time = int(time.time() - stop_time)
        logger.trace('Step 4')
        logger.info(f"Container stop after {stop_time}s")

        assert stop_time<=30,"Containers is not stop within 60sec"
    finally:
        preinstalled_meter.command("dbus-send --system --dest=com.itron.museplatform.ContainerManager /com/itron/museplatform/ContainerManager com.itron.museplatform.ContainerManager.Refresh")
        logger.trace('Step 5')
        refresh_time=time.time()
        stop = time.time() + (40)
        while time.time()<=stop:
            """
            Process is stop and wait for restart again
            """
            if is_process_running(preinstalled_meter,"lxc-start"):
                break
            time.sleep(3)
        assert is_process_running(preinstalled_meter,"lxc-start"),"timeout error waiting for conditions"
        refresh_time = int(time.time() - refresh_time)
        logger.info(f"Container refresh after {refresh_time}s")
    
        logger.trace('Step 6')
        assert refresh_time<=30,"Containers is not refersh within 60sec"
