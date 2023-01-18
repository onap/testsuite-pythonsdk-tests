from .settings import *

import json
from pathlib import Path

from onaptests.utils.resources import get_resource_location

CLEANUP_FLAG = True

ANCHOR_DATA = json.dumps({
    "bookstore": {
      "bookstore-name": "Chapters",
      "categories": [
        {
          "code": 1,
          "name": "SciFi",
          "books": [
              {
                "title": "2001: A Space Odyssey",
                "price": 5
              },
              {
                "title": "Dune",
                "price": 5
              }
          ]
        },
        {
          "code": 2,
          "name": "Kids",
          "books": [
              {
                "title": "Matilda"
              }
            ]
        }
      ]
    }
  })
ANCHOR_NAME = "basic-cps-test-anchor"
DATASPACE_NAME = "basic-cps-test-dataspace"
SCHEMA_SET_NAME = "basic-cps-test-schema-set"
SCHEMA_SET_FILE = Path(get_resource_location("templates/artifacts/cps/bookstore.yang"))

SERVICE_NAME = "Basic CPS test"
SERVICE_COMPONENTS = "CPS"
