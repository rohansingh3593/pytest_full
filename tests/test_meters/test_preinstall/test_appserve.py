import pytest
from tests.test_meters.utils import verify_appserve,sql_tables_no_as
from tests.test_meters.utils import install_agent, ParallelMeterWithDebug,V7_AGENT,DI_TEST_AGENT
from tests.test_meters.utils import HAN_AGENT,DI_TEST_AGENT,V7_AGENT,V7_CLONE_AGENT,P2P_AGENT,Third_Party_PubSub_AGENT,METROLOGY_DATA_AGENT,ITRONPUBSUBAGENT2


@pytest.mark.disable_changed
@pytest.mark.regress_ci
@pytest.mark.parametrize("check_hash", [False])
def test_verify_appserve(workdir, preinstalled_meter, di_version, logger, check_hash):
    logger.trace("%s using meter %s", __name__, preinstalled_meter.meter_name)

    fwver, asver = preinstalled_meter.version_info()
    logger.info("FW version: %s", fwver)
    logger.info("DI Version: %s", asver)
    verify_appserve(logger, preinstalled_meter, workdir, di_version, sql_tables_no_as=sql_tables_no_as, check_hash=check_hash)


#@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.disable_changed
#@pytest.mark.suite_id("2762299")
#@pytest.mark.test_case("2364678")
def test_case_verify_manifest(preinstalled_meter, logger, di_version):
    list = preinstalled_meter.command(f"cat /usr/share/itron/sha/appservicesLR.manifest")
    logger.info("manifest file is %s lines long", len(list))
    assert(len(list) > 10)



#@pytest.mark.regress_nightly
@pytest.mark.disable_changed
@pytest.mark.parametrize("agent_info", [HAN_AGENT,DI_TEST_AGENT,V7_AGENT,V7_CLONE_AGENT,P2P_AGENT,Third_Party_PubSub_AGENT,METROLOGY_DATA_AGENT,ITRONPUBSUBAGENT2])
def test_agent_install(preinstalled_meter, logger, agent_info):
    install_agent(preinstalled_meter, logger, agent_info)
    preinstalled_meter.gmr()


