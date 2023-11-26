import pytest
from itron.meter.Gen5Meter import ParallelMeter
import itron.meter.FwMan as FwMan
import itron.meter.AsMan as AsMan
import tests.test_meters.utils as utils
import os
import re

FW_VER='10.5.545'
FUTURE_ASVER='1.7.295.0'
AS_1_5 = '1.5.317.0'

legacy_upgrade = {
'10.2.536.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.2.536.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_11_30_0400_ps.zip',
'10.3.955.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.3.955.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_59_21_04_00_ps.zip',
'10.4.559.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.4.559.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_33_22_0400_ps.zip',
'10.5.542.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_ETMAd_SecureBoot_FW10.5.542.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_20_17_04_00_ps.zip',
}

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize("try_fw_ver", ['10.2.536.1','10.3.955.1','10.4.559.1','10.5.542.1'])
def test_diff_past(workdir,di_package,di_version, try_fw_ver, meter, logger):
    """ install old copy of firmware and as, then upgrade to latest.
    """
    logger.info("%s using meter %s", __name__, meter)
    top = AsMan.get_gittop()
    prev_fw_ver = try_fw_ver
    fw_image = os.path.join(top, legacy_upgrade[try_fw_ver])


    with ParallelMeter(meter,logger) as remote_meter:

        di_scripts = os.path.join( os.path.dirname(di_package), 'Diff_Scripts_' + os.path.basename(di_package))
        repacked_diff = remote_meter.repack_diff_package(logger, fw_image, di_package, di_scripts, workdir)

        matches = re.search("FW(10[0123456789.]+)",fw_image)
        logger.info("Testing %s", matches.group(1))
        assert prev_fw_ver == matches.group(1)

        utils.clean_as_and_gmr(logger, remote_meter, workdir)
        logger.info("Coldstarting to %s", prev_fw_ver)
        assert remote_meter.coldstart(version=prev_fw_ver, gmr=False, downgrade=True) == 0, "Failed coldstart"

        fwver, asver = remote_meter.version_info()
        assert fwver == prev_fw_ver
        assert asver is None
        sql_tables_no_as = remote_meter.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_no_as.json"))

        #diff_image = FwMan.get_build(version=current_fw_ver,diff_upgrade=True)
        utils.install_all_from_preinstall(logger,remote_meter)

        fwver, asver = remote_meter.version_info()
        assert fwver == prev_fw_ver
        assert asver is not None
        logger.info("Preinstall DI installed with version %s", asver)

        # now we should have an older version of HAN and AS installed
        tables = utils.verify_appserve(logger, remote_meter, workdir, asver, sql_tables_no_as)

        # finally, install a new version of DI using diff upgrade
        logger.info("Diff install with DI Package: %s", di_package)
        assert remote_meter.install(file=repacked_diff) == 0, "Failed diff upgrade install"
        fwver, asver = remote_meter.version_info()
        logger.info("DI version: %s", asver)
        sql_tables_with_as2 = remote_meter.sql_query( '.tables', json_file=utils.numbered_file(workdir, "sql_tables_with_as.json"))
        assert di_version == asver
        #assert set(sql_tables_with_as) == set(sql_tables_with_as2)

    return True

