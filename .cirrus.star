load("cirrus", "env")


def main(ctx):
    package_name = "git+https://github.com/Cog-Creators/Red-DiscordBot"
    if env["CIRRUS_BRANCH"] == "main":
        package_name = "Red-DiscordBot"
    elif env["CIRRUS_BRANCH"] != "dev":
        package_name += "@refs/{0}/merge".format(env["CIRRUS_BRANCH"])

    return [("env", {"RED_PACKAGE_NAME": package_name})]
