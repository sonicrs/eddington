import matplotlib.pyplot as plt
from pytest_cases import fixture


@fixture
def mock_figure(mocker):
    return mocker.patch.object(plt, "figure").return_value


@fixture
def mock_plt_show(mocker):
    return mocker.patch.object(plt, "show")
