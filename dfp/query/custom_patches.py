from dfp.model.Patch import Patch2, PARAM_MATCHER, TRANSFORM_BEFORE

CUSTOM_PATCHES = [
    # Changes maintainer instructions to label, e.g.: MAINTAINER John email@email.com ---> LABEL maintainer="John email@email.com"
    Patch2(
        before=f"MAINTAINER{PARAM_MATCHER}",
        after=f"LABEL",
        is_combinable=False,
        single_transform=None,
        group_transform=f"maintainer=\"{TRANSFORM_BEFORE}\""
    ),
    # Change add to copy
    Patch2(
        before=f"ADD{PARAM_MATCHER}",
        after=f"COPY",
        is_combinable=False,
        single_transform=None,
        group_transform=None
    ),
    # Update CMD to use JSON format
    Patch2(
        before=f"CMD{PARAM_MATCHER}",
        after=f"CMD",
        is_combinable=False,
        single_transform=f"\"{TRANSFORM_BEFORE}\"",
        group_transform=f"[{TRANSFORM_BEFORE}]",
        group_delimiter=", "
    ),
    # Update ENTRYPOINT to use JSON format
    Patch2(
        before=f"ENTRYPOINT{PARAM_MATCHER}",
        after=f"ENTRYPOINT",
        is_combinable=False,
        single_transform=f"\"{TRANSFORM_BEFORE}\"",
        group_transform=f"[{TRANSFORM_BEFORE}]",
        group_delimiter=", "
    ),
]
