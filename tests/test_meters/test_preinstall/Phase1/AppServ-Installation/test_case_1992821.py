"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992821
===================================================================================================
Test Case      : 1992821
Description    : Verify there is no core file generated after successful upgrade
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 -
After the upgradation of AppServices package into the meter.  Check there is no core file generated
on the below mentioned path:\nls /mnt/pouch/coredumps

Step 2 -
There shouldn\'t be any core file generated


===================================================================================================


"""
import pytest

# AUTOGENERATED Test Case 1992821

# @pytest.mark.skip(reason="TODO: test may not delete files in coredumps direcory: https://dev.azure.com/itron/RnD/_workitems/edit/2956422")
@pytest.mark.regress_nightly
@pytest.mark.slow1020 # test takes 10 to 20 minutes
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990123")
@pytest.mark.test_case("1992821")
def test_case(preinstalled_meter, logger,di_package_2k):
    logger.trace("Executing Test Case 1992821 - Verify there is no core file generated after successful upgrade")

    logger.trace('Step 1')
    dir="/mnt/pouch/coredumps"
    initial_list = preinstalled_meter.ls(dir)
    preinstalled_meter.install(file=di_package_2k)
    final_list=preinstalled_meter.ls(dir)

    logger.trace('Step 2')
    assert initial_list.sort() == final_list.sort(),"Core file is generated in /mnt/pouch/coredumps directory"




