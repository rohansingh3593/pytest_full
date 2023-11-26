
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase3/Install Script CPU and RAM Limits to DS/Phase3 Sanity - Cgroups
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2138877
===================================================================================================
Test Case      : 2138877
Description    : Verify CGroups exists in /sys/fs/
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : Completing Pull Request 154794 and the associated work items.
Steps:
===================================================================================================
Step 1 - 
cd /sys/fs press enter

Step 2 - 
cggroup folder exists


===================================================================================================


"""
import pytest

# AUTOGENERATED Test Case 2138877

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
#@pytest.mark.regress_smoke
@pytest.mark.suite_id("2385935")
@pytest.mark.test_case("2138877")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2138877 - Verify CGroups exists in /sys/fs/")
    logger.trace('Step 1')
    cgroup=preinstalled_meter.ls("/sys/fs")
    #logger.trace('Step 2')
    assert "cgroup" in cgroup[0]

    
    

