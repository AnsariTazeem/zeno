# CI

[Checks](../.github/workflows/checks.yml) runs the offline suite on
Windows for pushes and pull requests. Dependencies and actions are pinned.
Logs are retained for seven days.

To run the native controls, open **Actions → Checks → Run workflow** and enable
**native**. That job bootstraps a fresh environment, downloads the pinned public
assets and runs the five controls. Its time limit is 30 minutes. Qualification
<!-- coderabbit-ai-generated:v1 -->

<!-- coderabbit-ai-generated-section:v1:126c29d76abc276d0a03278f628f2ac436927783021f02940eae3edb307ea03a -->

results and raw logs from `eval_core_v6/runs/` are uploaded as artifacts.

<!-- /coderabbit-ai-generated:v1 -->

The workflow has read-only repository permissions. Checkout does not retain
credentials. Neither job uses model credentials or makes model calls.

[Latest runs](https://github.com/AnsariTazeem/zeno/actions/workflows/checks.yml)
