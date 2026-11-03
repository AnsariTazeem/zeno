# CI

[Checks](../.github/workflows/checks.yml) runs the 57-test offline suite on
Windows for pushes and pull requests. Dependencies and actions are pinned.
Logs are retained for seven days.

To run the native controls, open **Actions → Checks → Run workflow** and enable
**native**. That job bootstraps a fresh environment, downloads the pinned public
assets and runs the five controls. Its time limit is 30 minutes. Qualification
results and raw logs are uploaded as artifacts.

The workflow has read-only repository permissions. Checkout does not retain
credentials. Neither job uses model credentials or makes model calls.

[Latest runs](https://github.com/AnsariTazeem/zeno/actions/workflows/checks.yml)
