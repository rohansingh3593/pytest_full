"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992816
===================================================================================================
Test Case      : 1992816
Description    : Verify the ApplicationServices version is updated through iLID after successful upgrade
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check this Lid value before installation of AppServices package using the below command
Helper-CmdList.sh -r ILID_APP_SERVICE_PKG_INSTALLED | cut -d '=' -f 2

Step 2 - 
This should return the value as \"False\"


Step 3 - 
 AppServ Upgrade via ImProv

Step 4 - 

Step 5 -
After the successful AppServices package installed. Check the LID using the below command.
Helper-CmdList.sh -r ILID_DATASERVER_APPSERV_FW_VERSION | cut -d '=' -f 2

Step 6 - 
Installed Version of AppServices should be printed

Step 7 - 
And then check the other lid as well using the below command
Helper-CmdList.sh -r ILID_APP_SERVICE_PKG_INSTALLED | cut -d '=' -f 2

Step 8 - 
This should return the value as "True"


===================================================================================================


"""
import pytest
from itron.meter.Gen5Meter import ParallelMeter

# AUTOGENERATED Test Case 1992816

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
@pytest.mark.slow1020 # test takes 10 to 20 minutes
#@pytest.mark.crosslynx_test
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990123")
@pytest.mark.test_case("1992816")
@pytest.mark.gmr_meter
def test_case(meter, logger, di_package, di_version):
    with ParallelMeter(meter,logger) as remote_meter:
        remote_meter.gmr()
        logger.trace('Step 1')
        std_out = remote_meter.command("Helper-CmdList.sh -r ILID_APP_SERVICE_PKG_INSTALLED | cut -d '=' -f 2")
        logger.trace('Step 2')
        assert "false" in std_out
        logger.trace('Step 3')
        remote_meter.install(file=di_package)
        logger.trace('Step 4')
        logger.trace('Step 5')
        std_out = remote_meter.command("Helper-CmdList.sh -r ILID_DATASERVER_APPSERV_FW_VERSION | cut -d '=' -f 2")
        assert std_out[0] == di_version
        logger.trace('Step 5')
        std_out = remote_meter.command("Helper-CmdList.sh -r ILID_APP_SERVICE_PKG_INSTALLED | cut -d '=' -f 2")
        assert  'true' in std_out

