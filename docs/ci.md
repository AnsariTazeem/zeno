# Automated checks

[checks.yml](../.github/workflows/checks.yml) defines a Windows job for pushes,
pull requests and manual runs. It installs the two hash-pinned test packages,
runs 57 offline checks and keeps the logs for seven days. It makes no model
calls and does not run the native simulator by default.

For a native check, open the repository's Actions tab, select **Checks**, choose
**Run workflow**, and enable **native**. That job creates a fresh environment,
downloads pinned public assets and runs the five native controls. It has a
30-minute limit. Raw qualification logs/results are retained as artifacts.
No model credentials or API keys are needed.

All actions are pinned to commit IDs. Checkout does not retain credentials,
and workflow permissions are limited to reading repository contents. The
manual native job depends on a passing offline job.

The workflow has been checked locally but has not run on GitHub. Nothing has
been pushed by this workflow. A completed native run on a hosted runner would
provide evidence beyond the current computer; a YAML file alone does not.

Definitions checked against the official sources on 3 November 2026:

- [Workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax).
- [checkout v6 pin](https://github.com/actions/checkout/commit/d23441a48e516b6c34aea4fa41551a30e30af803).
- [setup-python inputs](https://github.com/actions/setup-python/blob/ece7cb06caefa5fff74198d8649806c4678c61a1/action.yml).
- [upload-artifact inputs](https://github.com/actions/upload-artifact/blob/b7c566a772e6b6bfb58ed0dc250532a479d7789f/action.yml).
