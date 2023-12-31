"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992834
===================================================================================================
Test Case      : 1992834
Description    : Verify the install script has restarted cosemd via MCD
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
pid of cosemd will change after Appserv upgrade.# ps | grep -i cosem

Step 2 - \\itron\\RnD\\_git\\DI.AppServices.Test
cosem should have a new pid


===================================================================================================

"""
import pytest

# AUTOGENERATED Test Case 1992834
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.suite_id("1990123")
@pytest.mark.test_case("1992834")
def test_case(preinstalled_meter, logger,di_package_2k):
    logger.trace("Executing Test Case 1992834 - Verify the install script has restarted cosemd via MCD")
    logger.trace('Step 1')
    fwver, Prev_asver = preinstalled_meter.version_info()
    cosem_before=preinstalled_meter.command("ps | grep -i cosem")    
    pid1 = [i.split()[0]  for i in cosem_before if "cosemd" in i.split()[4]]
    logger.trace("Initial PID of cosemd:"+pid1[0])
    preinstalled_meter.install(file=di_package_2k)
    fwver, cur_asver = preinstalled_meter.version_info()
    assert Prev_asver != cur_asver,"Appserve is not upgraded properly"
    cosem_after=preinstalled_meter.command("ps | grep -i cosem")
    pid2 = [i.split()[0]  for i in cosem_after if "cosemd" in i.split()[4]]
    logger.trace("PID of cosemd after Appserve Upgrade :"+pid2[0])
    assert pid1[0] !=pid2[0],'after installation of appserver PID of cosemd is same'
   
