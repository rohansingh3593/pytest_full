
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2012059
===================================================================================================
Test Case      : 2012059
Description    : Verify dataserver is up and running after the installation
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Install the given software

Step 2 - 
Meter should update with given software

Step 3 - 
check data server status\nps | grep -i DataServer

Step 4 - 
Data server should be up and running# ps | grep -i datas\n 2223 dserver_ 19572 S
/usr/bin/02020001/DataServer_Daemon --username=dserver_u --groupname=dserver_g\n


===================================================================================================


"""
import pytest

# AUTOGENERATED Test Case 2012059

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2012056")
@pytest.mark.test_case("2012059")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2012059 - Verify dataserver is up and running after the installation")

    logger.trace('Step 1')
    """appserve is installed with preinstalled_meter fixture"""
    logger.trace('Step 2')
    stdout = preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_DATASERVER_APPSERV_FW_VERSION;"')
    appServe_version = stdout[0].split('=')
    assert appServe_version[1] == di_version,"Appserve is not installed"
    logger.trace('Step 3')
    stdout = preinstalled_meter.command('ps | grep -i DataServer')
    output = [x for x in stdout if('/usr/bin/' in x.split()[4] and 'DataServer_Daemon' in x.split()[4])]
    logger.trace('Step 4')
    assert len(output)!=0


