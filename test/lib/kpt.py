import datetime
import os

import downloads
import e2e


def download_kpt(version, gcloud=None, statedir=None):
    now = datetime.datetime.utcnow()
    now = now.replace(microsecond=0)

    scratch_dir = os.path.join(
        e2e.workspace_dir(), "kpt-scratch-" + now.strftime("%Y%m%d%H%M%s")
    )

    bin_dir = os.path.join(scratch_dir, "bin")
    os.makedirs(bin_dir, exist_ok=True)

    url = "gs://kpt-dev/releases/v" + version + "/linux_amd64/kpt_linux_amd64-v"\
          + version + ".tar.gz"
    tarfile = os.path.join(scratch_dir, "kpt.tar.gz")
    gcloud.download_from_gcs(url, tarfile)  # TODO: caching?
    expanded = downloads.expand_tar(tarfile)
    kpt_path = os.path.join(bin_dir, "kpt")
    os.symlink(os.path.join(expanded, "kpt"), kpt_path)
    downloads.exec(["chmod", "+x", kpt_path])

    return Kpt(kpt_path, statedir=statedir)


def local_kpt(statedir=None):
    return Kpt("kpt", statedir=statedir)


class Kpt(object):
    def __init__(self, bin, statedir=None, env=None):
        if env is None:
            env = os.environ.copy()
        self.bin = os.path.expanduser(bin)
        self.env = env
        self.statedir = statedir

    def __repr__(self):
        s = "Kpt:" + self.bin
        if self.statedir:
            s = s + " statedir=" + self.statedir
        return s

    def get(self, src, dest):
        stdout = self.exec(["pkg", "get", src, dest])
        return stdout

    def set(self, path, k, v):
        stdout = self.exec(["cfg", "set", path, k, v])
        return stdout

    def list(self, path):
        stdout = self.exec(["cfg", "list-setters", path])
        return stdout

    def exec(self, args):
        return downloads.exec(
            [self.bin] + args, cwd=self.statedir, env=self.env
        ).strip()
