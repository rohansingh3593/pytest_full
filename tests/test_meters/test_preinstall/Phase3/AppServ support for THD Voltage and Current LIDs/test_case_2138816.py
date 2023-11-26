
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase3
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2138816
===================================================================================================
Test Case      : 2138816
Description    : Verify if the new LID values are accessible using the Transaction Process command
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : Completing Pull Request 154794 and the associated work items.
Steps:
===================================================================================================
Step 1 - 
Add appropriate load to the meter

Step 2 - 


Step 3 - 
 TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDV_A;\"\n

Step 4 - 
Should be accessible and prints the percentage of THD in Voltage in Phase Aeg:
RESULT:SUCCESS:ILID_INS_THDV_A:Real=0.0352999991082470

Step 5 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDV_B;\"

Step 6 - 
Should be accessible and prints the actual Voltage in Phase B

Step 7 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDV_C;\"

Step 8 - 
Should be accessible and prints the actual Voltage in Phase C

Step 9 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDI_A;\"

Step 10 - 
Should be accessible and prints the Current in Phase A

Step 11 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDI_B;\"

Step 12 - 
Should be accessible and prints the Current in Phase B

Step 13 - 
TransactionProcess --event=\"MUSE_V1;ReadLid;ILID_INS_THDI_C;\"

Step 14 - 
Should be accessible and prints the Current in Phase C


===================================================================================================


"""
import pytest
from tests.test_meters.rohan_utils import absolute_command
# AUTOGENERATED Test Case 2138816

@pytest.mark.skip(reason="THD_SKIPPED_DUE TO METER ISSUE")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2138769")
@pytest.mark.test_case("2138816")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2138816 - Verify if the new LID values are accessible using the Transaction Process command")


    # TODO: TEST NEEDS TRANSLATED
    # result=preinstalled_meter.command("some command on meter")
    #assert False

    logger.trace('Step 1')
    ILID_INS_THDV_A = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDV_A";')
    ILID_INS_THDV_A = float(ILID_INS_THDV_A[0].split("=")[1])
    ILID_INS_THDV_B = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDV_B";')
    ILID_INS_THDV_B = float(ILID_INS_THDV_B[0].split("=")[1])
    ILID_INS_THDV_C = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDV_C";')
    ILID_INS_THDV_C = float(ILID_INS_THDV_C[0].split("=")[1])
    logger.trace('Step 2')
    ILID_INS_THDI_A = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDI_A";')
    ILID_INS_THDI_A = float(ILID_INS_THDI_A[0].split("=")[1])
    ILID_INS_THDI_B = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDI_B";')
    ILID_INS_THDI_B = float(ILID_INS_THDI_B[0].split("=")[1])
    ILID_INS_THDI_C = absolute_command(preinstalled_meter,'TransactionProcess --event="MUSE_V1;ReadLid;ILID_INS_THDI_C";')
    ILID_INS_THDI_C = float(ILID_INS_THDI_C[0].split("=")[1])
    logger.trace("Step 3")
    assert (ILID_INS_THDV_A >= 0.0) & (ILID_INS_THDV_B >= 0.0) & (ILID_INS_THDV_C >= 0.0) & (ILID_INS_THDI_A >= 0.0) & (ILID_INS_THDI_B >= 0.0) & (ILID_INS_THDI_C >= 0.0), 'unable to access the LIDS' 
    assert (ILID_INS_THDV_A > 0.0) | (ILID_INS_THDV_B > 0.0) | (ILID_INS_THDV_C > 0.0), 'voltage is not proper'