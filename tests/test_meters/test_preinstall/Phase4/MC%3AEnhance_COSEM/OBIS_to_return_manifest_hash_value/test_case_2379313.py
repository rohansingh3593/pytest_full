
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379313
===================================================================================================
Test Case      : 2379313
Description    : Verify the installation of latest AppServ package
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install the latest appserv package using ImprovHelper or FDM. Verify the installed package using the
below command: # TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;\"

Step 2 - 
# TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;\"\nRESULT:SUCCESS
:ILID_DATASERVER_APPSERV_FW_VERSION:String=1.5.74.0

Step 3 - 


Step 4 - 


Step 5 - 



===================================================================================================


"""
import pytest
import re
from tests.test_meters.utils import  install_agent_and_activate, DI_TEST_AGENT

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379244")
@pytest.mark.test_case("2379313")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2379313 - Verify the installation of latest AppServ package")
  # preinstalled_meter function installing latest appserv package
    logger.trace('Step 1')
    
    logger.trace('Step 2')
    software_version=preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
    assert software_version[0].split("=")[1] == di_version

    




    

