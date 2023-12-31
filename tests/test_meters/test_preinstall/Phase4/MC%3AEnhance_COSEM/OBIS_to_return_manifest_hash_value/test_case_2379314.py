
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379314
===================================================================================================
Test Case      : 2379314
Description    : Ensure all services are running after Appserv installation
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify if all the daemons(dataserver,cosemd,containermanager) are up and running after the
Application Service FW version is updated.# ps | grep -i datas# ps | grep -i contain# ps | grep -i
cosem

Step 2 - 
All the services should be up and running.


===================================================================================================


"""
import pytest
from tests.test_meters.utils import  is_process_running


# AUTOGENERATED Test Case 2379314

@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.suite_id("2379244")
@pytest.mark.test_case("2379314")
def test_case(preinstalled_meter, logger, di_package_2k, di_version_2k):
    logger.trace("Executing Test Case 2379314 - Ensure all services are running after Appserv installation")
    logger.trace('Step 1')    
    preinstalled_meter.install(file=di_package_2k)
    fwver, asver = preinstalled_meter.version_info()
    assert asver == di_version_2k
    assert is_process_running(preinstalled_meter, 'DataServer_Daemon'), "DataServer_Daemon is not up"
    assert is_process_running(preinstalled_meter,'cosemd'),"cosemd is not up "
    assert is_process_running(preinstalled_meter, 'ContainerManager'), "ContainerManager is not up "