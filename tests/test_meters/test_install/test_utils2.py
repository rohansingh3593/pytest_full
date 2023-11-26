from itron.meter.Gen5Meter import ParallelMeter
import itron.meter.AsMan as AsMan
import pytest
from tests.test_meters.utils import verify_appserve, sql_tables_no_as
import os


@pytest.mark.disable_changed
@pytest.mark.parametrize("check_hash", [False])
def test_verify_appserve2(workdir, meter, logger, check_hash):
    logger.trace("%s using meter %s", __name__, str(meter))

    with ParallelMeter(meter, logger) as m:
        fwver, asver = m.version_info()
        logger.info("FW version: %s", fwver)
        logger.info("DI Version: %s", asver)
        verify_appserve(logger, m, workdir, asver, sql_tables_no_as=sql_tables_no_as, check_hash=check_hash)


@pytest.mark.disable_changed
@pytest.mark.skip("Need to updated the sql_tables list")
def test_verify_appserve(workdir,meter, logger):
    """ if appserve is installed, verify that it is.
        if it is not installed, check for cleanup """
    logger.trace("%s using meter %s", __name__, meter)

    with ParallelMeter(meter,logger) as m:

        fwver, asver = m.version_info()
        logger.info("FW version: %s", fwver)
        logger.info("DI Version: %s", asver)

        sql_tables_with_as = ["AgentData", "AgentEvents", "AgentFeatureDataCounter", "AgentInformation", "AgentMailbox",
        "AgentPolicy", "AgentRegistration", "BINARYSTORE", "Blurt", "BlurtBackup", "CATEGORY_TO_EVENTS", "CATEGORY_TO_LIDS",
        "CONFIGURATIONXML", "CONTAINEROVERLAY", "CONTAINERSETUP", "CONTAINERSTATUS", "CORRECTOWNERSHIP", "ComponentGroups",
        "Configuration", "ConfigurationPackage", "CpcRecord", "DATABASEMAINTENANCE", "DBusToEvent", "DEVICE_TO_LIDS",
        "DIDevice", "DIP2PGroupDbTable", "DIP2PKeyManagementDbTable", "DIP2PKeyValidationCounterDbTable",
        "DIP2PPublishedDataDbTable", "DIP2PReceivedNetworkMessagesDbTable", "DIP2PSentNetworkMessagesDbTable",
        "DIP2PStatSummaryTotalDbTable", "DIP2PStatsDatainCBORPerDay", "DIP2PSubscribedDataDbTable", "DIP2PSubscriptionDbTable",
        "DIPolicyFile", "DISPLAYLINES", "DISPLAYSCREENS", "DLMSACCESSRIGHTS", "DLMSCLIENTS", "DLMSOBJECTSTRUCTURE",
        "DLMSSERVERS", "DSTPERIODS", "DemandCapture", "DemandCoincident", "DemandCoincidentConfig", "DemandConfiguration",
        "DemandCumulative", "DemandPeaks", "DemandPrevious", "DemandReset", "DemandSetConfiguration", "DemandSetEventTime",
        "DeviceArchive", "DeviceArchiveEntry", "DisconnectTable", "DlmsConnections", "DlmsCosemGen5Roles", "DlmsFrameCounter",
        "DlmsSecuritySetup", "DlmsServerAssociations", "DynamicConfiguration", "ENERGYCONFIGURATION", "ENERGYDATA",
        "ENERGYHISTORY", "ERRORS", "EVENT_ACTION_STATS", "EVENT_CATEGORIES", "EVENT_STATS", "EventAction", "EventDescription",
        "EventLogID", "EventSpecification", "FWINFORMATION", "FeatureConfiguration", "GENERICLOOKUP", "GPRFILES", "HANACL",
        "HDLCCONNECTIONS", "HwControlTable", "IMAGETRANSFERBLOCK", "IMAGETRANSFERSTATUS", "ImageActivateInfo", "ImageProcessStatus",
        "ImageProcessTask", "LIDS", "LID_BEHAVIOR_TYPES", "LID_CATEGORIES", "LOG_EVENTRECORDS", "LOG_EVENTRULES",
        "LOG_EVENTRULES_TO_LISTENERSET_ASSOCIATIONS", "LOG_LISTENERSETS", "LOG_LISTENERS_TO_LISTENERSETS_ASSOCATIONS",
        "LidBehavior", "MESSAGESTORE", "OBIS", "OBISCLASSATTRIBUTES", "OBJECTSTORE", "OVERLAYCONFIGURATION", "OVERLAYSETUP",
        "PLUGINS", "PLUGINS_CATEGORY_TO_NAME", "PLUGINS_INTERFACE_TO_CATEGORY", "PREINSTALLPACKAGELIST", "PREINSTALLPACKAGEPREREQ",
        "PROFILEHISTORY", "PolicyViolationStatistics", "ProfileFlag", "ProfileInterval", "ProfileIntervalMain", "ProfileSetSpec",
        "PulseWeightTable", "RAMTABLENAMES", "RESETREASONS", "REVERTREASONS", "ReactorPriorityTable", "ReactorSetTable",
        "SELFREADBILLINGDATA", "SELFREADQUANTITYCONFIGURATION", "SELFREADRECORDS", "STATISTICS", "STATISTICS2", "SelfReadHistory",
        "SelfReadSchedule", "TABLESTOUCHES", "TESTHISTORY", "TamperTable", "TimeProfile", "TouDayProfileTable", "TouEnergyTable",
        "TouRateLookupTable", "TouSeasonProfileTable", "TouSingleValuesTable", "TouSpecialDaysTable", "TouWeekProfileTable",
        "VersionHistory"]

        verify_appserve(logger, m, workdir, asver, sql_tables_no_as=sql_tables_no_as)

legacy_upgrade = {
'10.2.536.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.2.536.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_11_30_0400_ps.zip',
'10.3.955.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.3.955.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_59_21_04_00_ps.zip',
'10.4.559.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_KETUMAd_SecureBoot_FW10.4.559.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T07_33_22_0400_ps.zip',
'10.5.542.1':'pytest/tests/test_install/diff-packages/signed-Test_FWDL_ETMAd_SecureBoot_FW10.5.542.1-10.5.611.1.AsicTestSecure_Gen5RivaAsic.sp_ASDIFF_Revert_Workarounds_Dev.tar.gz_2022_06_09T08_20_17_04_00_ps.zip',
}

@pytest.mark.disable_changed
@pytest.mark.need_di_package
@pytest.mark.parametrize("fw_ver", ['10.2.536.1','10.3.955.1','10.4.559.1','10.5.542.1'])
@pytest.mark.skip("ota pack not supported yet")
def test_verify_repack(workdir,di_package,fw_ver, meter, logger):
    """ verify repack works correctly """

    with ParallelMeter(meter,logger) as m:
        top = AsMan.get_gittop()

        fw_image = os.path.join(top, legacy_upgrade[fw_ver])

        di_scripts = os.path.join( os.path.dirname(di_package), 'Diff_Scripts_' + os.path.basename(di_package))
        repacked = m.repack_diff_package(logger, fw_image, di_package, di_scripts, workdir)

        #assert m.install(file=repacked) == 0, "Error upgrading from old version"


