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
                tar.extractall()
                os.chdir(os.listdir()[0])
                shutil.rmtree("redbot")

    for args in (
        (sys.executable, "-m", "pip", "install", "-U", f"{package_name}[test]"),
        (sys.executable, "-m", "pytest"),
    ):
        subprocess.run(args, check=True)


if __name__ == "__main__":
    asyncio.run(main())