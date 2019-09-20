body='
{
  "request": {
    "message": "Updating index for new_package 0.3.0",
    "branch": "master",
    "config": {
      "env": {
        "PACKAGE_VERSION": "0.3.0",
        "REPO_URL": "https://github.com/rporres/new_package",
        "PACKAGE_NAME": "new_package",
        "PYTHON_VERSION": "3.6.0",
      }
    }
  }
}
'

curl -s -X POST \
 -H "Content-Type: application/json" \
 -H "Accept: application/json" \
 -H "Travis-API-Version: 3" \
 -H "Authorization: token $TRAVIS_TOKEN" \
 -d "$body" \
 https://api.travis-ci.org/repo/rporres%2Fpython-package-server/requests
