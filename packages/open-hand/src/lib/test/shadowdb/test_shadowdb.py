import pytest
import os

from lib.predef.config import setenv
from lib.predef.consts import PRJ_ROOT_PATH

from lib.shadowdb.mongoconn import MongoDB
from lib.shadowdb.queries import QueryAPI, getQueryAPI


@pytest.fixture(autouse=True)
def env_setup():
    confPath = PRJ_ROOT_PATH / "conf" / "config-test.json"
    os.environ["config"] = str(confPath)
    setenv("testing")


@pytest.fixture(autouse=True)
def mongodb_setup(mongoDB: MongoDB):
    mongoDB.reset_db()


@pytest.fixture
def mongoDB():
    return MongoDB()


@pytest.fixture
def queryAPI():
    return getQueryAPI()


class TestShadowDB:
    def test_equivalence_table(self, queryAPI: QueryAPI):
        eq0 = queryAPI.create_equivalence(["a", "b", "c"])
        assert sorted(eq0) == ["a", "b", "c"]

        eq1 = queryAPI.create_equivalence(["x", "y"])
        assert sorted(eq1) == ["x", "y"]

        equivAs = queryAPI.find_equivalence(["a"])
        assert equivAs == eq0

        queryAPI.create_equivalence(["a", "y"])
        equivAs = queryAPI.find_equivalence(["c"])
        assert sorted(equivAs) == ["a", "b", "c", "x", "y"]
