
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1990751
===================================================================================================
Test Case      : 1990751
Description    : Retriveing the Applicationservice component version from the endpoint database.
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Retrival of the ApplicationService component version from Sqlite database using SQL query.
\nTransactionProcess --event=\"MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION\"

Step 2 - 
The ApplicationService component version should be
RESULT:SUCCESS:ILID_DATASERVER_APPSERV_FW_VERSION:String=1.0.9.0


===================================================================================================


"""
import pytest

# AUTOGENERATED Test Case 1990751

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1990124")
@pytest.mark.test_case("1990751")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 1990751 - Retriveing the Applicationservice component version from the endpoint database.")

    logger.trace('Step 1')
    as_version = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION"')
    as_version = as_version[0].split('=')
    logger.trace('Step 2')
    assert as_version[1] == di_version

