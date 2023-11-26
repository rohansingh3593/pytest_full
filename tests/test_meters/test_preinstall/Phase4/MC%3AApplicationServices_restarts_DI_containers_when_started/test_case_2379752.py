
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379752
===================================================================================================
Test Case      : 2379752
Description    : Installation of supported AppServices , ensure lxc PID
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install required A7 and AppServices

Step 2 - 
TP command should show the A7 (10.3) and AppServices1.3(1.5.x)

Step 3 - 
Install an Agent and ensure the PID of lxc container.

Step 4 - 
ps | grep -i lxc should be available

Step 5 - 
Load another AppService version which is supported

Step 6 - 
TP command should be updated with the newly installed AppServ version

Step 7 - 
Check if the PID is renewed

Step 8 - 
ps | grep -i lxc should be updated with new ID


===================================================================================================


"""
import pytest
from tests.test_meters.utils import DI_TEST_AGENT,install_agent_and_activate,is_process_running,wait_for_agents,refresh_container,filter_ps,Active_Containers,wait_for_agents

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379530")
@pytest.mark.test_case("2379752")
def test_case(preinstalled_meter, logger, di_version,di_package_2k,di_version_2k):
    logger.trace("Executing Test Case 2379752 - Installation of supported AppServices , ensure lxc PID")
    logger.trace('Step 1') 
    logger.trace('Step 2')
    software_version=preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
    assert software_version[0].split("=")[1] == di_version
    logger.trace('Step 3')
    agent = DI_TEST_AGENT
    install_agent_and_activate(preinstalled_meter,logger,agent)
    assert is_process_running(preinstalled_meter,"lxc-start"),"Containers is not running"
    logger.trace('Step 4')
    agent_pid_before=filter_ps(preinstalled_meter,f'{agent.name}_Daemon')[0][0]
    preinstalled_meter.install(file = di_package_2k)
    logger.trace('Step 5')
    software_version=preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
    logger.trace('Step 6')
    assert software_version[0].split("=")[1] == di_version_2k
    logger.trace('Step 7')
    wait_for_agents(preinstalled_meter, logger, [agent], 20*60)
    assert is_process_running(preinstalled_meter,"lxc-start"),"Containers is not running"
    agent_pid_after=filter_ps(preinstalled_meter,f'{agent.name}_Daemon')[0][0]
    logger.trace('Step 8')
    assert agent_pid_after!=agent_pid_before


