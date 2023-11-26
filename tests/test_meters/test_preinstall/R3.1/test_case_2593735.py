import pytest
import zipfile
import zipfile
import glob
import os
import tarfile

@pytest.mark.regress_nightly
@pytest.mark.regress_smoke
@pytest.mark.suite_id("2593734")
@pytest.mark.test_case("2593735")
def test_case_2593735(decrypted_di_package, logger, di_package, workdir):
    # Step 1: post di_package to http://ral-rdpwsgi-01.itron.com/fwdl-decrypter
    # unzip DI-AppServices-Package.{version}.zip

    files = glob.glob(os.path.join(decrypted_di_package, "*"), recursive=True)

    with tarfile.open(
        name = os.path.join(decrypted_di_package, "DI-AppServices.tar.bz2"),
        mode = "r:bz2") as tarball:
        tarball.extractall(workdir)

    """
        Expected Results:
        1. DI-AppServices.tar/DI-AppServices/etc/init.d/GAMed
        2. DI-AppServices.tar/DI-AppServices/etc/dbus-1/system.d/GAMed-dbus.conf
        3. DI-AppServices.tar/DI-AppServices/etc/monit.d/GAMed.monitrc
        4. DI-AppServices.tar/DI-AppServices/etc/GAMed_commit.txt
        5. DI-AppServices.tar/DI-AppServices/etc/GAMed_version.txt
    """
    verify_files = ["etc/init.d/GAMed", "etc/dbus-1/system.d/GAMed-dbus.conf","etc/monit.d/GAMed.monitrc",
        "etc/GAMed_commit.txt", "etc/GAMed_version.txt"]

    for file in verify_files:
        check_file = os.path.join(workdir, file)
        logger.info("Checking for %s in DI-AppServices.tar.bz2", check_file)
        assert os.path.exists(check_file)
        assert os.stat(check_file).st_size > 0
        logger.info("found file with %d bytes", os.stat(check_file).st_size)


