import pytest


@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2762299")
@pytest.mark.test_case("2751546")
@pytest.mark.revision("1")
def test_ads_integration_pass2(record_property,logger):
    logger.info("This is a test of regression fail")
    assert False

@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2762299")
@pytest.mark.test_case("2751546")
@pytest.mark.revision("1")
def test_ads_integration_pass2(record_property,logger):
    logger.info("This is a test of regression pass")
    assert True
