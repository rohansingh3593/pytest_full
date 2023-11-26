
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase2
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2050435
===================================================================================================
Test Case      : 2050435
Description    : Verify the installation of latest AppServ package with DI-Agent provided by the Agent team using ImProv method
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Do a GMR

Step 2 - 


Step 3 - 
Install the latest appserv package using the command: ImProvHelper.sh --image <DI Appserv.tar.gz>

Step 4 - 
Check using these two command if its installed with the latest Version: TransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_APP_SERVICE_PKG_INSTALLED;\"\nTransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION\"

Step 5 - 
Install the agent (eg: DItest agent) either using FDM or ImProvHelper.sh

Step 6 - 
Agent should be up and running with its PID and agent name.ps | grep Agent




===================================================================================================


"""
import pytest
from itron.meter.Gen5Meter import ParallelMeter
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT,wait_for_agents,is_process_running,filter_ps

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2050431")
@pytest.mark.gmr_meter
@pytest.mark.slow1020
@pytest.mark.test_case("2050435")
@pytest.mark.parametrize("agent_info", [DI_TEST_AGENT])
def test_case(meter, logger, di_package,di_version,agent_info):
    with ParallelMeter(meter,logger) as remote_meter:
        logger.trace("Executing Test Case 2050435 - Verify the installation of latest AppServ package with DI-Agent provided by the Agent team using ImProv method")
        logger.trace('Step 1')
        remote_meter.gmr()

        logger.trace('Step 2')
        logger.trace('Step 3')
        remote_meter.install(file=di_package)
        
        logger.trace('Step 4')
        std_out1=remote_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_APP_SERVICE_PKG_INSTALLED;"')
        std_out1=std_out1[0].split("=")[-1]
        assert "true" in std_out1, "APP_SERVICE_PKG is not INSTALLED"

        std_out2=remote_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
        std_out2=std_out2[0].split("=")[-1]
        assert di_version in std_out2, "it is not installed with the latest Version"

        logger.trace('Step 5')
        install_agent_and_activate(remote_meter,logger,agent_info)
        
        logger.trace('Step 6')
        assert is_process_running(remote_meter,f'{agent_info.name}_Daemon'),"Agent is not up "
        agent_pid=filter_ps(remote_meter,f'{agent_info.name}_Daemon')[0][0]
        assert int(agent_pid) > 0,"Agent is not running with valid PID"


      
