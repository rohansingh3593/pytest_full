
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379689
===================================================================================================
Test Case      : 2379689
Description    : Validate the Process ID of container
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Refer to: 2380395 - Install Appservices

Step 1 - 
Install the latest appserv package using ImprovHelper or FDM. Verify the installed package using the
below command:                                                  \n\nTransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION\"

Step 2 - 
Should return the installed AppService version ;

Step 3- 
After successful installation of AppService 1.3, there should not be PID for lxc (container)

Step 4 - 
ps | grep -i lxc - should not return the PID


Step 5 - 
nstall any Agent, and confirm if the PID is updated for LXC
(after signed_ConvertToLicensedMode-Package or SwitchDIInit.sh -s)

Step 6 -
ps | grep -i lxc - should return PID

Step 7- 
DataServer should be UP.




===================================================================================================


"""
import pytest
import time
from itron.meter.Gen5Meter import ParallelMeter
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT,wait_for_agents,is_process_running,Active_Containers,filter_ps

# AUTOGENERATED Test Case 2379689

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_weekly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379530")
@pytest.mark.test_case("2379689")
def test_case(meter, logger,di_version,di_package):
    logger.trace("Executing Test Case 2379689 - Validate the Process ID of container")

    #Refer to: 2380395 - Install Appservices
    logger.trace('Step 1')
    with ParallelMeter(meter,logger) as remote_meter:
        remote_meter.gmr()
        code = remote_meter.install(file = di_package)
        assert code ==0
        logger.trace('Step 2')
        logger.trace('Step 3')
        software_version=remote_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
        assert software_version[0].split("=")[1] == di_version
        logger.trace('Step 4')
        assert not is_process_running(remote_meter,"lxc-start"),'Container is still present.'
        logger.trace('Step 5')
        agent = DI_TEST_AGENT
        install_agent_and_activate(remote_meter,logger,agent)
        assert is_process_running(remote_meter,f'{agent.name}_Daemon'),"Agent not properly Functinoal"
        logger.trace('Step 6')
        assert is_process_running(remote_meter,"lxc-start"),'Container is up and runing'
        logger.trace('Step 7')
        assert is_process_running(remote_meter,f"DataServer_Daemon"),'DataServer is not be UP.'


