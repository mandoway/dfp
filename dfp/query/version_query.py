import requests

NOT_FOUND = "not found"


# example response: https://api.npms.io/v2/package/react
def npmFetchLatestVersion(pkg_name: str) -> str:
    """
    Fetches the latest version of a npm package from npms.io
    :param pkg_name: package to search for
    :return: latest version of the package or 'not found' if error was returned
    """
    base_url = "https://api.npms.io/v2"
    request = f"{base_url}/package/{pkg_name}"

    response = requests.get(request)
    if response.status_code == requests.codes.ok:
        json = response.json()
        newest_version = json["collected"]["metadata"]["version"]
    else:
        newest_version = NOT_FOUND

    return newest_version


# example response: https://pypi.org/pypi/sampleproject/json
def pipFetchLatestVersion(pkg_name: str) -> str:
    """
    Fetches the latest version of a python package from pypi.org
    :param pkg_name: package to search for
    :return: latest version of the package or 'not found' if error was returned
    """
    base_url = "https://pypi.org/pypi"
    request = f"{base_url}/{pkg_name}/json"

    response = requests.get(request)
    if response.status_code == requests.codes.ok:
        json = response.json()
        newest_version = json["info"]["version"]
    else:
        newest_version = NOT_FOUND

    return newest_version


# example response: https://hub.docker.com/v2/repositories/library/ubuntu/tags?ordering=last_updated
def dockerFetchLatestVersion(image_name: str) -> list[str]:
    """
    Fetches the latest version of a docker image from hub.docker.com
    :param image_name: image to search for
    :return: list of version suggestions for the image or 'not found' if error was returned
    """
    base_url = "https://hub.docker.com/v2/repositories/library"
    request = f"{base_url}/{image_name}/tags"
    params = {
        "ordering": "last_updated",
        "name": "."
    }

    version_list = []
    response = requests.get(request, params=params)
    if response.status_code == requests.codes.ok:
        json = response.json()
        version_list = list(
            map(lambda i: i["name"], json["results"])
        )[:5]

    if len(version_list) == 0:
        version_list = [NOT_FOUND]
    else:
        del params["name"]
        response = requests.get(request, params=params)
        if response.status_code == requests.codes.ok:
            json = response.json()
            version_list += list(
                map(lambda i: i["name"], json["results"])
            )[:5]

    return sorted(sorted(list(set(version_list)), reverse=True), key=lambda it: _isfloat(it), reverse=True)


def _isfloat(val):
    try:
        float(val)
        return True
    except ValueError:
        return False


"""
Map of supported package managers.
Values are tuple of version delimiter and getLatestVersion function
"""
SUPPORTED_PM = {
    "npm": ("@", npmFetchLatestVersion),
    "pip": ("==", pipFetchLatestVersion)
}
