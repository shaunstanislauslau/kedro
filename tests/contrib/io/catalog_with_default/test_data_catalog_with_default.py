# Copyright 2018-2019 QuantumBlack Visual Analytics Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND
# NONINFRINGEMENT. IN NO EVENT WILL THE LICENSOR OR OTHER CONTRIBUTORS
# BE LIABLE FOR ANY CLAIM, DAMAGES, OR OTHER LIABILITY, WHETHER IN AN
# ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF, OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# The QuantumBlack Visual Analytics Limited (“QuantumBlack”) name and logo
# (either separately or in combination, “QuantumBlack Trademarks”) are
# trademarks of QuantumBlack. The License does not grant you any right or
# license to the QuantumBlack Trademarks. You may not use the QuantumBlack
# Trademarks or any confusingly similar mark as a trademark for your product,
#     or use the QuantumBlack Trademarks in any other manner that might cause
# confusion in the marketplace, including but not limited to in advertising,
# on websites, or on software.
#
# See the License for the specific language governing permissions and
# limitations under the License.

# pylint: disable=unused-import
import pytest

from kedro.contrib.io.catalog_with_default import DataCatalogWithDefault
from kedro.io import CSVLocalDataSet, DataCatalog, MemoryDataSet
from tests.io.conftest import dummy_dataframe, filepath  # NOQA
from tests.io.test_data_catalog import data_set, sane_config  # NOQA


def default_csv(name):
    return CSVLocalDataSet(name)


def test_load_from_unregistered(dummy_dataframe, tmpdir):  # NOQA
    catalog = DataCatalogWithDefault(data_sets={}, default=default_csv)

    path = str(tmpdir.mkdir("sub").join("test.csv"))
    catalog.save(path, dummy_dataframe)
    reloaded_df = catalog.load(path)

    assert dummy_dataframe.equals(reloaded_df)


def test_save_and_load_catalog(data_set, dummy_dataframe, tmpdir):  # NOQA
    catalog = DataCatalogWithDefault(data_sets={"test": data_set}, default=default_csv)

    path = str(tmpdir.mkdir("sub").join("test"))
    catalog.save(path, dummy_dataframe)
    reloaded_df = catalog.load(path)
    assert dummy_dataframe.equals(reloaded_df)


def test_from_sane_config(sane_config):  # NOQA
    with pytest.raises(
        ValueError, match="Cannot instantiate a `DataCatalogWithDefault`"
    ):
        DataCatalogWithDefault.from_config(
            sane_config["catalog"], sane_config["credentials"]
        )


def test_from_sane_config_default(sane_config, dummy_dataframe, tmpdir):  # NOQA
    catalog = DataCatalog.from_config(
        sane_config["catalog"], sane_config["credentials"]
    )
    catalog_with_default = DataCatalogWithDefault.from_data_catalog(
        catalog, default_csv
    )
    path = str(tmpdir.mkdir("sub").join("missing.csv"))
    catalog_with_default.save(path, dummy_dataframe)
    reloaded_df = catalog_with_default.load(path)
    assert dummy_dataframe.equals(reloaded_df)


def test_default_none():
    with pytest.raises(
        TypeError,
        match="Default must be a callable with a "
        "single input string argument: the "
        "key of the requested data set.",
    ):
        DataCatalogWithDefault(data_sets={}, default=None)


# pylint: disable=unused-argument
def default_memory(name):
    return MemoryDataSet(5)


def test_remember_load():
    catalog = DataCatalogWithDefault(
        data_sets={}, default=default_memory, remember=True
    )
    assert catalog.load("any") == 5
    assert "any" in catalog.list()


def test_remember_save(tmpdir, dummy_dataframe):  # NOQA
    catalog = DataCatalogWithDefault(data_sets={}, default=default_csv, remember=True)

    path = str(tmpdir.mkdir("sub").join("test.csv"))
    catalog.save(path, dummy_dataframe)
    assert tmpdir.join("sub").join("test.csv") in catalog.list()
