load("cirrus", "env")

load("github.com/cirrus-modules/graphql", "failed_instruction", "rerun_task")


def main(ctx):
    package_name = "git+https://github.com/Cog-Creators/Red-DiscordBot"
    if env["CIRRUS_BRANCH"] == "main":
        package_name = "Red-DiscordBot"
    elif env["CIRRUS_BRANCH"] != "dev":
        package_name += "@refs/{0}/merge".format(env["CIRRUS_BRANCH"])

    return [("env", {"RED_PACKAGE_NAME": package_name})]


def on_task_failed(ctx):
    if ctx.payload.data.task.automaticReRun:
        print("Task is already an automatic re-run, let's not retry...")
        return
    instruction = failed_instruction(ctx.payload.data.task.id)
    if not instruction or not instruction["logsTail"]:
        print("Couldn't find any logs for last failed command.")
        return

    should_rerun = False
    logs = instruction["logsTail"]
    task_name = instruction["name"]

    # task-specific ignores
    if task_name == "install_instructions":
        for line in logs:
            if (
                # observed with dnf on Alma Linux and Fedora (GCE images)
                line == "Errors during downloading metadata for repository 'google-cloud-sdk':"
                # observed with dnf on RHEL derivatives
                or line.startswith("Cannot retrieve metalink for repository: ")
                # observed with zypper on openSUSE Tumbleweed
                or line.endswith("does not contain the desired medium")
            ):
                should_rerun = True
                break

    # global ignores
    if not should_rerun:
        for line in logs:
            # Observed while trying to build Python with install_instructions on Arch Linux
            # as well as with install_python_with_pyenv on OSes that use pyenv.
            if "curl: (56)" in line:
                should_rerun = True
                break

    if should_rerun:
        print("Found failed log line indicating a transient issue!")
        new_task_id = rerun_task(ctx.payload.data.task.id)
        print("Successfully re-ran task! Here is the new one: {}".format(new_task_id))
    else:
        print("Didn't find any transient issues in logs!")
