from parser.index_html_parser import IndexHTMLParser
from pathlib import Path
import subprocess
import tempfile
import sys
import os
import re

# Check environment variables
for var in ["PACKAGE_VERSION", "REPO_URL", "PACKAGE_NAME", "PYTHON_VERSION", "GITHUB_TOKEN"]:
    missing = False
    if not os.environ.get(var):
        print("Missing env var {}".format(var))
        missing = True

if missing:
    sys.exit(1)

repo_tag = os.environ.get("REPO_TAG", "v{}".format(os.environ["PACKAGE_VERSION"]))
gh_remote_url = "https://{}@github.com/rporres/python-package-server.git".format(
        os.environ["GITHUB_TOKEN"])
target_branch = os.environ.get("TARGET_BRANCH", "master")

# Normalize name
# See https://www.python.org/dev/peps/pep-0503/#normalized-names
normalized = re.sub(r"[-_.]+", "-", os.environ["PACKAGE_NAME"]).lower()
index_file = os.path.join("docs", normalized, "index.html")
index_file_abs = os.path.join(os.path.dirname(__file__), "..", index_file)

links_data = []
if os.path.exists(index_file_abs):
    print("Using existing file %s" % index_file_abs)
    parser = IndexHTMLParser()
    links_data = parser.get_index_data(Path(index_file_abs).read_text())

links_data.append({
    "href": "git+{repo_url}@{repo_tag}#egg={package_name}-{package_version}".format(
                repo_url=os.environ["REPO_URL"],
                repo_tag=repo_tag,
                package_version=os.environ["PACKAGE_VERSION"],
                package_name=os.environ["PACKAGE_NAME"]),
    "data-requires-python": "&gt;={}".format(os.environ["PYTHON_VERSION"]),
    "data": "-".join([os.environ["PACKAGE_NAME"], os.environ["PACKAGE_VERSION"]])
})


lt = '<a href="{}" data-requires-python="{}">{}</a><br/>'
links = [ lt.format(d["href"], d["data-requires-python"], d["data"]) for d in links_data ]
doc = '''<!DOCTYPE html>
<html>
<head>
<title>Links for {package}</title>
</head>
<body>
<h1>Links for {package}</h1>
{links}
</body>
</html>
'''.format(package=os.environ["PACKAGE_NAME"], links="\n".join(links))

# push to github
with tempfile.TemporaryDirectory() as tmpdir:
    subprocess.run(["git", "config", "user.name", "Infra sourced{d}"], check=True)
    subprocess.run(["git", "config", "user.email", "infra@sourced.tech"], check=True)
    os.chdir(tmpdir)
    subprocess.run(["git", "clone", "--branch={}".format(target_branch), "--depth=1",
            gh_remote_url, "."], check=True)

    if not os.path.exists(index_file):
        os.mkdir(os.path.dirname(index_file))

    with open(index_file, 'w') as f:
        f.write(doc)

    subprocess.run(["git", "add", "-A"], check=True)
    subprocess.run(["git", "commit", "-sm", "Update index for {}".format(normalized)], check=True)
    subprocess.run(["git", "push", gh_remote_url, "{}:{}".format(target_branch, target_branch)],
            check=True)
