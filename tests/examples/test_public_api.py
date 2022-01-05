"""
This file was adapted from mock_autogen/tests/test_public_api.py and modified.
"""
from tests.examples.code_snippets import os_remove_wrap, process_and_zip
from tests.test_utils import safe_assert_clipboard

MOCKED_DEPENDENCIES_HEADER = "# mocked dependencies\n"
MOCKED_FUNCTIONS_HEADER = "# mocked functions\n"
MOCKED_WARNINGS_HEADER = "# warnings\n"
PREPARE_ASSERTS_CALLS_HEADER = (
    "# calls to generate_asserts, put this after the 'act'\nimport mock_autogen\n"
)


def test_generate_uut_mocks_simple(mocker, capsys, mg):
    expected = """# mocked dependencies
mock_remove = mocker.MagicMock(name='remove')
mocker.patch('tests.examples.code_snippets.os.remove', new=mock_remove)
"""

    # Arrange
    generated = mg.generate_uut_mocks(os_remove_wrap)
    exec(generated)  # verify the validity of generated mocks code

    # Act
    os_remove_wrap("some/non/existing/path")  # this fails if not mocked

    # Assert
    assert expected == generated

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)


def test_generate_uut_mocks_complex(mocker, capsys, mg):
    expected = """# mocked dependencies
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.examples.code_snippets.zipfile.ZipFile', new=mock_ZipFile)
"""

    # Arrange
    generated = mg.generate_uut_mocks(process_and_zip)
    exec(generated)  # verify the validity of generated mocks code

    # Act
    process_and_zip(
        "", "in_zip.txt", "foo bar"  # this fails if not mocked - path can't be empty
    )

    # Assert
    assert expected == generated

    # verify additional side affects like print to console and clipboard
    assert generated in capsys.readouterr().out
    safe_assert_clipboard(generated)


def test_generate_asserts_simple(mocker, capsys, mg):
    # Arrange
    mock_something = mocker.MagicMock(name="something")

    # Act
    mock_something.call_something()

    # Assert
    generated_wo_name = mg.generate_asserts(mock_something)
    generated_with_name = mg.generate_asserts(mock_something, name="mock_something")

    expected = "mock_something.call_something.assert_called_once_with()"
    assert expected == generated_wo_name.rstrip()
    assert generated_wo_name == generated_with_name

    # verify additional side affects like print to console and clipboard
    assert expected in capsys.readouterr().out
    safe_assert_clipboard(expected)

    exec(generated_wo_name)  # verify the validity of generated assertions code


def test_generate_asserts_complex(mocker, capsys, mg):
    # Arrange
    # mocked functions
    mock_ZipFile = mocker.MagicMock(name="ZipFile")
    mocker.patch("tests.examples.code_snippets.zipfile.ZipFile", new=mock_ZipFile)

    # Act
    process_and_zip(
        "", "in_zip.txt", "foo bar"  # this fails if not mocked - path can't be empty
    )
    # Assert
    generated_wo_name = mg.generate_asserts(mock_ZipFile)
    generated_with_name = mg.generate_asserts(mock_ZipFile, name="mock_ZipFile")
    expected = """assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)"""
    assert expected == generated_wo_name.rstrip()
    assert generated_wo_name == generated_with_name

    # verify additional side affects like print to console and clipboard
    assert expected in capsys.readouterr().out
    safe_assert_clipboard(generated_with_name)

    exec(generated_wo_name)  # verify the validity of generated assertions code


def test_generate_uut_mocks_with_asserts_simple(mocker, capsys, mg):
    expected_uut_mocks_with_asserts = """# mocked dependencies
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.examples.code_snippets.zipfile.ZipFile', new=mock_ZipFile)
# calls to generate_asserts, put this after the 'act'
mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')
"""

    # Arrange
    generated = mg.generate_uut_mocks_with_asserts(process_and_zip)
    (
        generated_warnings,
        generated_mocks,
        generated_asserts,
    ) = _extract_warnings_generated_mocks_and_generated_asserts(generated)
    exec("\n".join(generated_mocks))

    # Act
    process_and_zip(
        "", "in_zip.txt", "foo bar"  # this fails if not mocked - path can't be empty
    )
    exec("\n".join(generated_asserts))

    # verify the validity of generated asserts code
    expected_actual_asserts = """assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)"""

    # verify additional side affects like print to console and clipboard
    assert expected_actual_asserts in capsys.readouterr().out
    safe_assert_clipboard(expected_actual_asserts)

    exec(expected_actual_asserts)  # verify the validity of generated assertions code

    # Assert
    assert expected_uut_mocks_with_asserts == generated


def _extract_warnings_generated_mocks_and_generated_asserts(expected):
    warnings = []
    generated_mocks = []
    generated_asserts = []
    inside_warnings = False
    inside_mocks = False
    inside_asserts = False
    for line in expected.splitlines():
        if line == MOCKED_WARNINGS_HEADER.rstrip():
            inside_warnings = True
        if (
            line == MOCKED_FUNCTIONS_HEADER.rstrip()
            or line == MOCKED_DEPENDENCIES_HEADER.rstrip()
        ):
            inside_warnings = False
            inside_mocks = True
        if line == PREPARE_ASSERTS_CALLS_HEADER.splitlines()[0]:
            inside_mocks = False
            inside_asserts = True
        if inside_warnings:
            warnings.append(line)
        if inside_mocks:
            generated_mocks.append(line)
        if inside_asserts:
            generated_asserts.append(line)
    return warnings, generated_mocks, generated_asserts
