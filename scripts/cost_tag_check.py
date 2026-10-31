"""
B2, part 2 — implement the cost-tagging check.

Read fixtures/plan.json for the shape of a `terraform show -json` plan: a `resource_changes`
list, where each entry has a `type`, an `address`, and `change.after.tags`.

Implement check_plan() so it:
  - Looks at every resource being created or changed (skip anything not in
    change.actions, e.g. a pure "no-op" / "read" change).
  - Fails (returns a non-zero exit code) if the resource is missing the tag that identifies
    the real billing unit, per README.md's domain model — not whatever tag the resource
    happens to already carry.
  - Is idempotent: running this twice against the same plan file produces the same result,
    with no duplicate output and no flipped pass/fail.
  - Prints which specific resource address(es) are missing the tag.

Run manually: python scripts/cost_tag_check.py fixtures/plan.json
"""
import json
import sys


def check_plan(plan_path: str) -> int:
    """
    Returns an exit code: 0 if every taggable resource being created/changed has
    landlord_account_id, non-zero otherwise.
    """

    with open(plan_path, "r") as f:
        plan = json.load(f)

    missing = []

    for resource in plan.get("resource_changes", []):

        actions = resource.get("change", {}).get("actions", [])

        # Skip no-op/read changes
        if not any(action in actions for action in ["create", "update", "replace"]):
            continue

        tags = (
            resource.get("change", {})
            .get("after", {})
            .get("tags", {})
        ) or {}

        if "landlord_account_id" not in tags:
            missing.append(resource["address"])

    if missing:
        print("Resources missing landlord_account_id tag:")
        for address in sorted(missing):
            print(f"- {address}")
        return 1

    print("All resources contain landlord_account_id tag.")
    return 0


if __name__ == "__main__":
    sys.exit(check_plan(sys.argv[1]))