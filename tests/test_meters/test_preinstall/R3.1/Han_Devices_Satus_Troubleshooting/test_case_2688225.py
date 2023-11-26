
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/R3.1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2688225
===================================================================================================
Test Case      : 2688225
Description    : Verify Non whitelist requests as per JSON data published
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_DATASERVER_HAN_STATS_NUM_NON_WHITELIST_REQS;\"

Step 2 - 
RESULT:SUCCESS:ILID_DATASERVER_HAN_STATS_NUM_NON_WHITELIST_REQS:U32=0

===================================================================================================

"""
import pytest
#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2688193")
@pytest.mark.test_case("2688225")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2688225 - Verify Non whitelist requests as per JSON data published")
    logger.trace('Step 1')
    output = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_HAN_STATS_NUM_NON_WHITELIST_REQS;"')
    logger.trace('Step 2')
    assert "RESULT:SUCCESS:ILID_DATASERVER_HAN_STATS_NUM_NON_WHITELIST_REQS" in output[0]



