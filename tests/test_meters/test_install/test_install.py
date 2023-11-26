"""

Meter example test

fixtures in pytest/tests/conftest.py provide:

workdir - working directory to store test based logs for triage.  this directory is co-located with test
di_package - the DI package from the current build (signed)
di_version - the version of the DI package in the current build
fw_version - version of the latest firmware

"""
from itron.meter.Gen5Meter import ParallelMeter
from itron.meter import AsMan
import pytest
from tests.test_meters.utils import diff_and_save, verify_appserve, diff_and_save, install_build, numbered_file
import os
import tests.test_meters.utils as utils

def reset_meter(m,logger,needed_fw_ver,workdir,caplog):
    utils.clean_as_and_gmr(logger, m, workdir)

    # coldstart meter to fw version
    logger.info("Coldstarting to %s", needed_fw_ver)
    fwver, asver = m.version_info()
    downgrade = needed_fw_ver != fwver
    assert m.coldstart(version=needed_fw_ver, gmr=False, downgrade=downgrade) == 0, "Failed coldstart"
    fwver, asver = m.version_info()
    assert fwver == needed_fw_ver
    assert asver is None
    sql_tables_no_as = m.sql_query( '.tables', json_file=numbered_file(workdir, "sql_tables_no_as.json"))
    return sql_tables_no_as

@pytest.mark.disable_changed
@pytest.mark.need_di_package
def test_install(workdir,di_package,di_version, meter,logger, current_fw_ver, caplog):
    """ coldstart the current firmware and install the current DI package """
    logger.info("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as m:

        sql_tables_no_as = reset_meter(m, logger, current_fw_ver, workdir, caplog)
        logger.info("DI Package: %s", di_package)

        # now install AppServe
        with caplog.at_level(logger.WARNING):
            assert m.install(file=di_package) == 0, "package install failed"
        fwver, asver = m.version_info()
        assert asver == di_version
        sql_tables_with_as = m.sql_query( '.tables', json_file=os.path.join(workdir, "sql_tables_with_as.json"))
        verify_appserve(logger, m, workdir, asver, sql_tables_no_as=sql_tables_no_as)

        diff_and_save(os.path.join(workdir, "new_tables.json"),
            sql_tables_no_as,
            sql_tables_with_as)

    return True


expected_tables_by_version = {
    '1.5.317.0': ["AgentData", "AgentEvents", "AgentFeatureDataCounter", "AgentInformation",
        "AgentMailbox", "AgentPolicy", "AgentRegistration", "DIDevice", "DIP2PGroupDbTable",
        "DIP2PPublishedDataDbTable",
        "DIP2PReceivedNetworkMessagesDbTable", "DIP2PSentNetworkMessagesDbTable", "DIP2PStatSummaryTotalDbTable",
        "DIP2PStatsDatainCBORPerDay", "DIP2PSubscribedDataDbTable", "DIP2PSubscriptionDbTable", "DIPolicyFile",
        "DeviceArchive", "DeviceArchiveEntry", "FeatureConfiguration", "PolicyViolationStatistics"],
    '1.3.470.0': ["AgentData", "AgentEvents", "AgentFeatureDataCounter", "AgentInformation",
        "AgentMailbox", "AgentPolicy", "AgentRegistration", "DIDevice", "DIP2PGroupDbTable",
         "DIP2PPublishedDataDbTable",
        "DIP2PReceivedNetworkMessagesDbTable", "DIP2PSentNetworkMessagesDbTable", "DIP2PStatSummaryTotalDbTable",
        "DIP2PStatsDatainCBORPerDay", "DIP2PSubscribedDataDbTable", "DIP2PSubscriptionDbTable", "DIPolicyFile",
        "DeviceArchive", "DeviceArchiveEntry", "FeatureConfiguration", "PolicyViolationStatistics"]
}


@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize("di_version_old", [
    #'1.3.470.0',
    '1.5.317.0'])
def test_upgrade_old(workdir, di_package,di_version, meter,logger, current_fw_ver, di_version_old, caplog):
    """ coldstart the current firmware and install the current DI package """
    logger.info("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as m:

        sql_tables_no_as = reset_meter(m, logger, current_fw_ver, workdir, caplog)

        # install older package
        di_package_old = AsMan.get_build(di_version_old)
        logger.info("Installing %s", di_package_old)
        with caplog.at_level(logger.WARNING):
            assert install_build(logger, workdir, m, di_package_old, di_version_old, expected_new_tables=
                expected_tables_by_version[di_version_old], sql_tables_no_as=sql_tables_no_as), "failed to install old DI build"

        # install current package
        logger.info("Installing %s", di_package)
        with caplog.at_level(logger.WARNING):
            assert install_build(logger, workdir, m, di_package,
                di_version, sql_tables_no_as=sql_tables_no_as), "failed to upgrade from old DI build"


    return True

@pytest.mark.disable_changed
@pytest.mark.need_di_package
#@pytest.mark.regress_weekly
def test_upgrade_prosession(workdir, di_package,di_version, meter,logger, current_fw_ver,caplog):
    """ coldstart the current firmware and install the current DI package """
    logger.info("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as m:

        sql_tables_no_as=reset_meter(m, logger, current_fw_ver, workdir, caplog)

        procession = [
            #TBD: this will not install '1.3.470.0',
            '1.5.317.0',
            '1.7.295.0'
            ]
        for ver in procession:
            # install older package
            di_package_old = AsMan.get_build(ver)
            assert di_package_old, "Error in test, can't find DI build on server mount /mnt/ral_"
            logger.info("Installing %s", di_package_old)
            with caplog.at_level(logger.WARNING):
                assert install_build(logger, workdir, m, di_package_old,
                    ver), "failed to install old package"
                assert install_build(logger, workdir, m, di_package_old, ver, expected_new_tables=
                    expected_tables_by_version[ver], sql_tables_no_as=sql_tables_no_as), "failed to install old DI build"

        # install current package
        logger.info("Installing %s", di_package)
        with caplog.at_level(logger.WARNING):
            assert install_build(logger, workdir, m, di_package,
                di_version), "failed to install current package over old"

    return True

@pytest.mark.disable_changed
#@pytest.mark.regress_weekly
#@pytest.mark.parametrize("meter_num", [x for x in range(4)])
def test_coldstart(meter, logger, current_fw_ver):
    with ParallelMeter(meter, logger) as m:

        fwver, asver = m.version_info()
        logger.trace("Current versions: fw:%s as:%s", fwver, asver)
        m.coldstart(version="10.5.770")
        fwver, asver = m.version_info()
        logger.trace("Current versions: fw:%s as:%s", fwver, asver)
        m.coldstart(version=current_fw_ver)
        fwver, asver = m.version_info()
        assert fwver == current_fw_ver
        logger.trace("TEST PASSED: Current versions: fw:%s as:%s", fwver, asver)


