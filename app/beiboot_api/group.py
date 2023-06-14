from typing import List, Tuple

GROUP_PREFIX = "getdeck-api-"
GROUP_DEFAULT = "default"
GROUPS = ["developer", "free", GROUP_DEFAULT]  # fixed set of groups


def group_filter_and_selection(x_forwarded_groups: str | None) -> Tuple[List[str], str]:
    if not x_forwarded_groups:
        return [], GROUP_DEFAULT

    if type(x_forwarded_groups) == str:
        x_forwarded_groups = x_forwarded_groups.replace(GROUP_PREFIX, "").split(",")

    groups_filtered = list(set(x_forwarded_groups) & set(GROUPS))

    if len(groups_filtered) == 0:
        group_selected = GROUP_DEFAULT
    else:
        for group in GROUPS:
            if group in groups_filtered:
                group_selected = group
                break
        else:
            group_selected = GROUP_DEFAULT

    return groups_filtered, group_selected
