"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/R3.1
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2672853
===================================================================================================
Test Case      : 2672853
Description    : Retrieval of hash value from cosem tool 
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Run cosem-test tool and check  the hex value output. # cosemtest getobis obis=0-128:96.20.19.255
attribute=2 class=1 sap=120

Step 2 - 
# cosemtest getobis obis=0-128:96.20.19.255 attribute=2 class=1\nRequesting class 1, OBIS
0-128:96.20.19.255 , Attribute2\n Result: Success[0] 02010A40343066383530653539383136653332613637353
36333386364303966643736396561383339303566316339373563353932326433356262316238313739636438\n


===================================================================================================


"""
import pytest
# @pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2672846")
@pytest.mark.test_case("2672853")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2672853 - Retrieval of hash value from cosem tool ")
    logger.trace('Step 1')
    costome_tool=preinstalled_meter.command('cosemtest getobis obis=0-128:96.20.19.255 attribute=2 class=1 sap=120')
    logger.trace('Step 2')
    costome_tool=" ".join(costome_tool)
    assert "Requesting class 1, OBIS 0-128:96.20.19.255 , Attribute2" in costome_tool
    assert "Result: Success[0]" in costome_tool
   
        


