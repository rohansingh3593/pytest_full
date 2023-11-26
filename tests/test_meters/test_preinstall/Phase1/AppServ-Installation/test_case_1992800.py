"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1992800
===================================================================================================
Test Case      : 1992800
Description    : Verify the configurable LID specific to timer(6 hours) is available for modification.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Check the LID is available to change from the default timer (6hours).\nTransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_PKG_MAINTENANCE_DELAY_SECS;\"

Step 2 - 
LID should be available for modification.\nReturn value: 21600 (secs)

Step 3 - 
Using the following command update the above lid to 1000 sec\nTransactionProcess
--event=\"MUSE_V1;WriteLid;ILID_PKG_MAINTENANCE_DELAY_SECS;1000\"

Step 4 - 
Change should be successful

Step 5 - 
Recheck the above LID using the below command\nTransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_PKG_MAINTENANCE_DELAY_SECS;\"

Step 6 - 
LID will show the modified value\nReturn value: 1000 (secs)



===================================================================================================
"""
import pytest
from tests.test_meters.lids import read_lid, write_lid

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990123")
@pytest.mark.test_case("1992800")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 1992800 - Verify the configurable LID specific to timer(6 hours) is available for modification.")
    mds = read_lid(preinstalled_meter, "ILID_PKG_MAINTENANCE_DELAY_SECS")
    assert "21600" in mds
    try:
        logger.trace('Step 1')
        std_out = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;WriteLid;ILID_PKG_MAINTENANCE_DELAY_SECS;21600"')
        assert "21600" in std_out[0]
        logger.trace('Step 2')
        std_out = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_PKG_MAINTENANCE_DELAY_SECS;"')
        assert "21600" in std_out[0]
        logger.trace('Step 3')
        std_out = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;WriteLid;ILID_PKG_MAINTENANCE_DELAY_SECS;1000"')
        assert "1000" in std_out[0]
        logger.trace('Step 5')
        std_out = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_PKG_MAINTENANCE_DELAY_SECS;"')
        assert "1000" in std_out[0]
    finally:
        write_lid(preinstalled_meter, "ILID_PKG_MAINTENANCE_DELAY_SECS", mds)






