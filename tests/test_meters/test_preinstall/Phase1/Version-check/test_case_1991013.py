"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1991013
===================================================================================================
Test Case      : 1991013
Description    : Ensure that the ApplicationService version is retained after soft reboot
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Ensuring the ApplicationService component version being retained after soft reboot.\nreboot

Step 2 - 
The ApplicationService component should be able to maintain the version.


===================================================================================================

"""
import pytest

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990124")
@pytest.mark.test_case("1991013")
 
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1991013 - Ensure that the ApplicationService version is retained after soft reboot")
    logger.trace('Step 1')
    apser1=preinstalled_meter.version_info()[1]
    preinstalled_meter.reboot_meter()
    logger.trace('Step 2')
    apser2=preinstalled_meter.version_info()[1]
    assert apser1==apser2,"The ApplicationService component is not able to maintain the version."
    


    
    




























    



