
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379682
===================================================================================================
Test Case      : 2379682
Description    : Verify the installation of latest AppServ package 
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

Step 3 - 
DataServer should be UP.

Step 4 - 



===================================================================================================


"""
import pytest
import time
from itron.meter.Gen5Meter import ParallelMeter
from tests.test_meters.utils import is_process_running,Active_Containers,filter_ps
#pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379530")
@pytest.mark.test_case("2379682")
def test_case(preinstalled_meter, logger,di_version,di_package):
    logger.trace("Executing Test Case 2379682 - Verify the installation of latest AppServ package ")
    #Refer to: 2380395 - Install Appservices
    logger.trace('Step 1')
    """preinstall_meter is Install Appservices"""
    logger.trace('Step 2')
    software_version=preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
    assert software_version[0].split("=")[1] == di_version
    logger.trace('Step 3')
    assert is_process_running(preinstalled_meter,f"DataServer_Daemon"),'DataServer is not be UP.'
    
    


