import pytest
from itron.meter.Gen5Meter import ParallelMeter
import itron.meter.FwMan as FwMan
import itron.meter.AsMan as AsMan
import tests.test_meters.utils as utils
import os

FUTURE_ASVER='1.7.295.0'
AS_1_5 = '1.5.317.0'
FW_VER='10.5.770.1'

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize('repacked_diff', ["fw_ver"], indirect=True)
def test_diff_no_di(workdir,di_package,di_version, repacked_diff, meter, logger, prev_fw_ver, current_fw_ver, request):
    """ install the previous version of fw, and apply the repacked diff upgrade,
        then validate that AS is running correctly """

    repacked_diff = request.getfixturevalue(repacked_diff)
    logger.info("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as remote_meter:

        utils.clean_as_and_gmr(logger, remote_meter, workdir)
        logger.info("Coldstarting to %s", prev_fw_ver)
        assert remote_meter.coldstart(version=prev_fw_ver, gmr=False) == 0, "Failed coldstart"

        fwver, asver = remote_meter.version_info()
        assert fwver == prev_fw_ver
        assert asver is None
        sql_tables_no_as = remote_meter.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_no_as.json"))

        #diff_image = FwMan.get_build(version=current_fw_ver,diff_upgrade=True)
        logger.info("DI Package: %s inside %s", di_package, repacked_diff)
        assert remote_meter.install(file=repacked_diff) == 0
        fwver, asver = remote_meter.version_info()
        assert fwver == current_fw_ver
        assert asver == di_version

        utils.verify_appserve(logger, remote_meter, workdir, asver,sql_tables_no_as)

    return True

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize('repacked_diff', ["fw_ver"], indirect=True)
def test_diff_with_di_newer(workdir,di_package,di_version, repacked_diff, meter, logger, prev_fw_ver, request):
    """
    test diff upgrade when DI.AppServe is already installed on the meter
    1) coldstart to previous fw
    2) install AS version
    3) diff upgrade
    4) verify result
    """
    logger.info("%s using meter %s", __name__, meter)
    repacked_diff = request.getfixturevalue(repacked_diff)

    with ParallelMeter(meter,logger) as remote_meter:

        utils.clean_as_and_gmr(logger, remote_meter, workdir)
        logger.info("Coldstarting to %s", prev_fw_ver)
        assert remote_meter.coldstart(version=prev_fw_ver, gmr=False) == 0, "Failed coldstart"
        fwver, asver = remote_meter.version_info()
        assert fwver == prev_fw_ver
        assert asver is None
        sql_tables_no_as = remote_meter.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_no_as.json"))

        # install a different DI package on the meter
        di_package_new = AsMan.get_build(FUTURE_ASVER)
        assert remote_meter.install(file=di_package_new) == 0, "Failed AppServe install"
        fwver, asver = remote_meter.version_info()
        logger.info("DI version: %s", asver)
        sql_tables_with_as = remote_meter.sql_query( '.tables', json_file=utils.numbered_file(workdir, "sql_tables_with_as.json"))

        # add the HAN Agent
        utils.install_han_from_preinstall(logger,remote_meter)

        # now, try to install the repackaged diff with the current AppServe
        logger.info("DI Package: %s", di_package)
        assert remote_meter.install(file=repacked_diff) == 0, "Failed diff upgrade install"
        fwver, asver = remote_meter.version_info()
        logger.info("DI version: %s", asver)
        sql_tables_with_as2 = remote_meter.sql_query( '.tables', json_file=utils.numbered_file(workdir, "sql_tables_with_as.json"))

        assert set(sql_tables_with_as) == set(sql_tables_with_as2)

        # should not have installed, as installed is newer
        assert asver != di_version, "should not have installed on the meter, as the AS version is lower"

        utils.verify_appserve(logger, remote_meter,
            workdir, asver, sql_tables_no_as=sql_tables_no_as)

    return True

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize('repacked_diff', ["fw_ver"], indirect=True)
def test_diff_with_di_older(workdir,di_package,di_version, repacked_diff, meter, logger, prev_fw_ver, request):
    """
    test diff upgrade when DI.AppServe is already installed on the meter
    1) coldstart to previous fw
    2) install AS version
    3) diff upgrade
    4) verify result
    """
    logger.info("%s using meter %s", __name__, meter)
    repacked_diff = request.getfixturevalue(repacked_diff)

    with ParallelMeter(meter,logger) as remote_meter:

        utils.clean_as_and_gmr(logger, remote_meter, workdir)
        logger.info("Coldstarting to %s", prev_fw_ver)
        assert remote_meter.coldstart(version=prev_fw_ver, gmr=False) == 0, "Failed coldstart"

        logger.info("DI Package: %s", di_package)
        fwver, asver = remote_meter.version_info()
        assert fwver == prev_fw_ver
        assert asver is None
        sql_tables_no_as = remote_meter.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_no_as.json"))

        # install a different DI package on the meter
        di_package_new = AsMan.get_build(AS_1_5)
        assert remote_meter.install(file=di_package_new) == 0, "Failed AppServe install"
        fwver, asver = remote_meter.version_info()
        logger.info("DI version: %s", asver)
        sql_tables_with_as_old = remote_meter.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_with_as_old.json"))

        # add the HAN Agent
        utils.install_han_from_preinstall(logger,remote_meter)

        # now, try to install the repackaged diff with the current AppServe
        assert remote_meter.install(file=repacked_diff) == 0, "Failed diff upgrade install"
        fwver, asver = remote_meter.version_info()
        logger.info("DI version: %s", asver)

        info = utils.verify_appserve(logger, remote_meter,
            workdir, asver, sql_tables_no_as=sql_tables_no_as)

        # set with diff older (will include extra items not in previous list)
        # assert set(sql_tables_with_as_old) == set(info['sql_tables_with_as'])
        assert asver == di_version

    return True

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.xfail
def test_short_fail(workdir,di_package,di_version, meter, logger, prev_fw_ver):
    """ quick test that will always fail, to demonstrate falure case """
    logger.info("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as remote_meter:

        fwver, asver = remote_meter.version_info()
        logger.info("FW Version: %s", fwver)
        logger.info("DI Version: %s", asver)
        assert False


