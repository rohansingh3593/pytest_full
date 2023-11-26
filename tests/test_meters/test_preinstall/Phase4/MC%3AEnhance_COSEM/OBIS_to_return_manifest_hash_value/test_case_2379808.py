
"""
REGENRATE: True
Set REGENERATE to False if you modify this comment
section to inhibit re-writing this section
===================================================================================================
Test Plan Path : templates/AppServ-TestRepository/Phase4
Test Case Link : https://dev.azure.com/itron/SoftwareProducts/_workitems/edit/2379808
===================================================================================================
Test Case      : 2379808
Description    : Verify the manifest hash value - sha256sum
Area Path      : RnD/GFW-IVV/DI Outcomes/APP-Serve
Iteration Path : RnD/3 Week
System.History : None
Steps:
===================================================================================================
Step 1 - 
Verify the manifest hash value obtained from cosemtool with the sha256 sum using the below command :
# sha256sum /usr//share/itron/sha/appservicesLR.manifest

Step 2 - 
# sha256sum /usr/share/itron/sha/appservicesLR.manifest
\na99735a0891eb8760e7fa17f24cd726c43243337d9300239c81ed8a99425b18f
/usr/share/itron/sha/appservicesLR.manifest

Step 3 - 
Cross-check with the cosem returned output

Step 4 - 
The hash values should match


===================================================================================================


"""
import pytest
import codecs

# AUTOGENERATED Test Case 2379808

#@pytest.mark.skip(reason="TODO: unimplemented test case")
@pytest.mark.regress_nightly
# @pytest.mark.regress_smoke
@pytest.mark.suite_id("2379244")
@pytest.mark.test_case("2379808")
def test_case(preinstalled_meter, logger, di_version):
    logger.trace("Executing Test Case 2379808 - Verify the manifest hash value - sha256sum")
    logger.trace('Step 1')
    
    logger.trace('Step 2')
    hash_cmd = 'sha256sum /usr//share/itron/sha/appservicesLR.manifest'
    hash1 = preinstalled_meter.command(hash_cmd)[0].split()[0]
    logger.info(hash1)
    logger.trace('Step 3')
    hash_from_obis = preinstalled_meter.command('cosemtest getobis obis=0-128:96.20.17.255 attribute=2 class=1 sap=120')[1].split(' ')[3]
    logger.info("hash from obis %s",type(hash_from_obis))
    hash_from_obis = str(codecs.decode(hash_from_obis, "hex"),'utf-8')[4:]
    logger.trace('Step 4')
    assert hash1 == hash_from_obis
