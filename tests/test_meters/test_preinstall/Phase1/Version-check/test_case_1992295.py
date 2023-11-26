
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992295
===================================================================================================
Test Case      : 1992295
Description    : Ensure that the ApplicationService version is retained after multiple reboots
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Ensuring the ApplicationService component version being retained after multiple reboots.

Step 2 - 
The ApplicationService component should be able to maintain the version.

Step 3 - 
Do a manual reboot of the meter.#reboot

Step 4 - 


Step 5 - 
After sometime when the meter is powered on, check the AppService version from the lid value -
#TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;\"

Step 6 - 
The lid should show the version of AppService installed already.


===================================================================================================


"""
import pytest

# AUTOGENERATED Test Case 1992295

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.slow1020 # test takes 10 to 20 minutes
@pytest.mark.suite_id("1990124")
@pytest.mark.test_case("1992295")
def test_case(preinstalled_meter, logger):
    logger.trace("Executing Test Case 1992295 - Ensure that the ApplicationService version is retained after multiple reboots")

    logger.trace('Step 1')
    asver = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;"')
    asver_before_reboot = asver[0].split('=')
    logger.trace('Step 2')
    logger.trace('Step 3')
    preinstalled_meter.reboot_meter()
    logger.trace('Step 4')
    preinstalled_meter.reboot_meter()
    logger.trace('Step 5')
    asver = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;"')
    asver_after_reboot = asver[0].split('=')
    logger.trace('Step 6')
    assert asver_before_reboot[1] == asver_after_reboot[1],"AppServe version not retained after multiple reboot"


