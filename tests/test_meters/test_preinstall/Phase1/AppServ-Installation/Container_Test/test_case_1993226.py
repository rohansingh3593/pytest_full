
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993226
===================================================================================================
Test Case      : 1993226
Description    : CMTotalWatchdogCount
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Ensure an agent is running in the Meter (any container) and lxc is up

Step 2 - 
ps | grep -i Agent  402 containe  6384 S    /usr/bin/0302ff84/MetrologyDataAgent_Daemon\nps | grep
-i lxc32660 containe  2032 S    lxc-start -d -P /tmp/container -n 50593792\n

Step 3 - 
Verify the watchdog count for the running container sqlite3 /tmp/muse01.db \"select
TotalWatchdogCount from CONTAINERSTATUS;\" \n

Step 4 - 
An integer value should be seen# sqlite3 /tmp/muse01.db \"select TotalWatchdogCount from
CONTAINERSTATUS;\" \n


===================================================================================================


"""
import pytest
import time
from tests.test_meters.utils import install_agent_and_activate,is_process_running,filter_ps,P2P_AGENT,Active_Containers

# AUTOGENERATED Test Case 1993226

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993226")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1993226 - CMTotalWatchdogCount")

    logger.trace('Step 1')
    install_agent_and_activate(preinstalled_meter,logger,P2P_AGENT)
    assert is_process_running(preinstalled_meter,"Agent")," Agent is not running"
    assert is_process_running(preinstalled_meter,"lxc-start")," Container is not running"

    logger.trace('Step 2')
    filter_ps(preinstalled_meter,"Agent")
    filter_ps(preinstalled_meter,"lxc-start")

    logger.trace('Step 3')
    active_contaiers=Active_Containers(preinstalled_meter)

    logger.trace('Step 4')
    for cid in active_contaiers:
        stop = time.time() + 5*60
        while time.time()<=stop:
            
            time_out=time.time() + 10
            while time_out>time.time():    
                code,WatchdogCount=preinstalled_meter.command_with_code(f'sqlite3 /tmp/muse01.db "select TotalWatchdogCount from CONTAINERSTATUS where Guid={cid}"')
                if code == 0:
                    break
                time.sleep(2)
            assert code == 0 ,"Watchdog command is not executed"

            if WatchdogCount :
                break
            else:
                time.sleep(5)
                
        assert WatchdogCount,"timeout for condition check"
        assert WatchdogCount[0].isnumeric(),f"the watchdog count for the running container {cid} is not a integer"