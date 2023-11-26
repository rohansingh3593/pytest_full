
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379321
===================================================================================================
Test Case      : 2379321
Description    : Ensure the ApplicationService version and hash are retained after meter reboot
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Reboot the meter

Step 2 - 
The ApplicationService component should be able to maintain the version and its manifest hash value


===================================================================================================


"""
import pytest

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2379244")
@pytest.mark.test_case("2379321")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 2379321 - Ensure the ApplicationService version and hash are retained after meter reboot")
    logger.trace('Step 1')
    
    apser1=preinstalled_meter.version_info()[1]
    hash_cmd = 'sha256sum /usr//share/itron/sha/appservicesLR.manifest'
    hash1 = preinstalled_meter.command(hash_cmd)[0].split()[0]
    preinstalled_meter.reboot_meter()
    logger.trace('Step 2')
    apser2=preinstalled_meter.version_info()[1]
    hash2 = preinstalled_meter.command(hash_cmd)[0].split()[0]
    assert apser1==apser2,"The ApplicationService component is not able to maintain the version."
    assert hash1==hash2,"The ApplicationService component is not able to maintain the hash value."

