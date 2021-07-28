import pyperclip


def safe_assert_clipboard(expected):
    """
    Asserts that the clipboard contains the expected string.
    If the clipboard is not available, ignores this test. This can happen on
    some Linux systems like the GitHub Action runners.
    Args:
        expected (str): the expected string that the clipboard should contain
    Raises:
        AssertionError: when the content of the clipboard does not match the
        expected
    """
    clipboard = None
    try:
        clipboard = "\n".join(pyperclip.paste().splitlines())
    except pyperclip.PyperclipException as e:
        pass
    if clipboard:
        cleaned_expected = "\n".join(expected.splitlines())
        assert cleaned_expected == clipboard
