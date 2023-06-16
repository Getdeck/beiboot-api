from typing import Annotated, List, Tuple

from fastapi import Depends
from settings import Settings, get_settings

GROUP_PREFIX = "getdeck-api-"


def group_filter_and_selection(
    x_forwarded_groups: str | None, settings: Annotated[Settings, Depends(get_settings)]
) -> Tuple[List[str], str]:
    groups = ["developer", "free", settings.group_default_name]  # fixed set of groups

    if not x_forwarded_groups:
        return [], settings.group_default_name

    if type(x_forwarded_groups) == str:
        x_forwarded_groups = x_forwarded_groups.replace(GROUP_PREFIX, "").split(",")

    groups_filtered = list(set(x_forwarded_groups) & set(groups))

    if len(groups_filtered) == 0:
        group_selected = settings.group_default_name
    else:
        for group in groups:
            if group in groups_filtered:
                group_selected = group
                break
        else:
            group_selected = settings.group_default_name

    return groups_filtered, group_selected
