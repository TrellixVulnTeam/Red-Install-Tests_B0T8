#!/usr/bin/env python3
import asyncio
import os
import shutil
import subprocess
import sys
import tarfile
from io import BytesIO

import aiohttp
import redbot


async def main() -> None:
    skip_tests = os.getenv("RED_SKIP_TESTS", "")
    if skip_tests:
        print("Running tests skipped. Reason:", skip_tests)
        raise SystemExit(0)

    package_name = os.environ["RED_PACKAGE_NAME"]
    os.mkdir("Red-DiscordBot")
    os.chdir("Red-DiscordBot")

    if package_name == "Red-DiscordBot":
        url = (
            f"https://files.pythonhosted.org/packages/source/R/Red-DiscordBot/"
            f"Red-DiscordBot-{redbot.__version__}.tar.gz"
        )
    else:
        url = package_name.rsplit("#", maxsplit=1)[0]

    if sys.platform == "win32":
        subprocess.run(("curl", "--head", url), check=True)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            fp = BytesIO(await resp.read())

            with tarfile.open(fileobj=fp, mode="r|gz") as tar:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner) 
                    
                
                safe_extract(tar)
                os.chdir(os.listdir()[0])
                shutil.rmtree("redbot")

    fast_import_path = (
        f"{os.path.dirname(redbot.__file__)}/pytest/downloader_testrepo.export"
    )

    # remove original-oid lines from git fast-import file as it doesn't work on Debian 10
    with open(fast_import_path, newline="\n") as fp:
        lines = []
        for line in fp:
            if not line.startswith("original-oid "):
                lines.append(line)

    with open(fast_import_path, "w", newline="\n") as fp:
        for line in lines:
            fp.write(line)

    for args in (
        (sys.executable, "-m", "pip", "install", "-U", f"{package_name}[test]"),
        (sys.executable, "-m", "pytest"),
    ):
        subprocess.run(args, check=True)


if __name__ == "__main__":
    asyncio.run(main())
