"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase1/AppServ-Installation
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/1993233
===================================================================================================
Test Case      : 1993233
Description    : ILID_MAX_MEMORY_LIMIT_Default_Value
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify the default value ILID_CONTAINER_MAX_MEMORY_LIMIT_KB TransactionProcess
--event=\"MUSE_V1;ReadLid;ILID_CONTAINER_MAX_MEMORY_LIMIT_KB

Step 2 - 
Default value ILID_CONTAINER_MAX_MEMORY_LIMIT_KB should match to the value defined in container
design document.


===================================================================================================


"""
import pytest

# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
 
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("1993280")
@pytest.mark.test_case("1993233")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 1993233 - ILID_MAX_MEMORY_LIMIT_Default_Value")
    logger.trace('Step 1')
    contain_memory_data=preinstalled_meter.command('TransactionProcess --event="MUSE_V1;ReadLid;ILID_CONTAINER_MAX_MEMORY_LIMIT_KB"')
    logger.trace('Step 2')
    assert 'RESULT:SUCCESS:ILID_CONTAINER_MAX_MEMORY_LIMIT_KB:U32=65000' in contain_memory_data


