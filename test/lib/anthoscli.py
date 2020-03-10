import datetime
import json
import os
import subprocess

import downloads
import e2e


def download_anthoscli(version, gcloud=None):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)

    scratch_dir = os.path.join(
        e2e.workspace_dir(), "anthoscli-scratch-" + now.strftime("%Y%m%d%H%M%s")
    )

    # We build up symlinks to the downloaded binaries in the bin directory
    bin_dir = os.path.join(scratch_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    url = (
        "gs://gke-on-prem-staging/anthos-cli/v"
        + version
        + "-gke.0/anthoscli_linux_amd64-"
        + version
        + ".tar.gz"
    )
    tarfile = os.path.join(scratch_dir, "anthoscli.tar.gz")
    gcloud.download_from_gcs(url, tarfile)  # TODO: caching?
    expanded = downloads.expand_tar(tarfile)
    anthoscli_path = os.path.join(bin_dir, "anthoscli")
    os.symlink(os.path.join(expanded, "anthoscli"), anthoscli_path)
    downloads.exec(["chmod", "+x", anthoscli_path])

    return AnthosCLI(anthoscli_path)


class AnthosCLI(object):
    def __init__(self, bin, env=None):
        if env is None:
            env = os.environ.copy()
        self.bin = os.path.expanduser(bin)
        self.env = env

    def __repr__(self):
        return "AnthosCLI:" + self.bin

    def version(self):
        version = self.exec(["version"])
        return version

    def apply(self, specdir):
        stdout = self.exec(["apply", "-f", specdir])
        return stdout

    def exec(self, args):
        return downloads.exec([self.bin] + args, env=self.env).strip()
