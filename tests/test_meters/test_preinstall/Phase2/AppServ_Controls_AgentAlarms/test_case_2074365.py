"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2074365
===================================================================================================
Test Case      : 2074365
Description    : Verify the ApplicationService behavior post reboot
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Ensure DataServer is running with AppServ Version a.b.c.e
Step 2 - 
# ps | grep -i datas\n22054 dserver_ 18484 R    /usr/bin/02020001/DataServer_Daemon
--username=dserver_u --groupname=dserver_g\n
Step 3 - 
Install DITest Agent and ensure it is functional
Step 4 - 
# ps | grep -i agent\n22535 containe  7232 S    /usr/bin/0302ff80/DITestAgent_Daemon\n
Step 5 - 
Reboot the Meter and ensure DataServer and Agent are running
Step 6 - 
# ps | grep -i datas\n22054 dserver_ 18484 R    /usr/bin/02020001/DataServer_Daemon
--username=dserver_u --groupname=dserver_g# ps | grep -i agent\n22535 containe  7232 S
/usr/bin/0302ff80/DITestAgent_Daemon
===================================================================================================
""" 
import pytest,time
from tests.test_meters.utils import install_agent_and_activate ,DI_TEST_AGENT,filter_ps,wait_for_agents, is_process_running
from tests.test_meters.rohan_utils import absolute_command
# AUTOGENERATED Test Case 2074365
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2062303")
@pytest.mark.test_case("2074365")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
#@pytest.mark.parametrize('execution_number', range(10))
def test_case(preinstalled_meter, logger, di_version,agent_info):

    logger.trace("Executing Test Case 2066958 - Verify the behavior ApplicationService when the ApplicationService  is upgraded from one version to another ")
    logger.trace('Step 1')
    stdout = absolute_command(preinstalled_meter, 'TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;"')
    app_version = stdout[0].split('=')
    assert app_version[1]==di_version
    
    logger.trace('Step 2')
    assert is_process_running(preinstalled_meter, "DataServer_Daemon"),"Dataserver is not running"

    logger.trace('Step 3')
    install_agent_and_activate(preinstalled_meter,logger,agent_info)
    logger.trace('Step 4')
    logger.trace('Step 5')
    preinstalled_meter.reboot_meter()
    logger.trace('Step 6')
    stop=time.time()+5*60
    while time.time()<=stop:
        stdout = is_process_running(preinstalled_meter, "DataServer_Daemon")
        if stdout:
            break
        time.sleep(10)
    assert stdout,"Dataserver is not running"
    wait_for_agents(preinstalled_meter, logger, [DI_TEST_AGENT], 20*60)

