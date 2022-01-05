# pytest-mock-generator

<div align="center">

[![Build status](https://github.com/pksol/pytest-mock-generator/workflows/build/badge.svg?branch=master&event=push)](https://github.com/pksol/pytest-mock-generator/actions?query=workflow%3Abuild)
[![Python Version](https://img.shields.io/pypi/pyversions/pytest-mock-generator.svg)](https://pypi.org/project/pytest-mock-generator/)

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-green.svg)](https://github.com/PyCQA/bandit)
[![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pksol/pytest-mock-generator/blob/master/.pre-commit-config.yaml)
[![Semantic Versions](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--versions-e10079.svg)](https://github.com/pksol/pytest-mock-generator/releases)
[![License](https://img.shields.io/github/license/pksol/pytest-mock-generator)](https://github.com/pksol/pytest-mock-generator/blob/master/LICENSE)

A pytest fixture wrapper for https://pypi.org/project/mock-generator

</div>

## Installation

```bash
pip install pytest-mock-generator
```

or install with [poetry](https://github.com/python-poetry/poetry):

```bash
poetry add pytest-mock-generator
```

## Usage
This [pytest plugin](https://docs.pytest.org/en/latest/how-to/writing_plugins.html) 
adds the `mg` [fixture](https://docs.pytest.org/en/latest/reference/fixtures.html#fixture)
which helps when writing tests that use [python mocks](https://docs.python.org/3.7/library/unittest.mock.html).

Let's start with an easy example. Assume you have a module named `tested_module.py` which holds a function
to process a string sent to it and then add it to a zip file:
```python
import zipfile

def process_and_zip(zip_path, file_name, contents):
    processed_contents = "processed " + contents  # some complex logic
    with zipfile.ZipFile(zip_path, 'w') as zip_container:
        zip_container.writestr(file_name, processed_contents)
```
This is the function that you want to test (aka Unit Under Test or UUT). 
You don't want to create a file on the hard drive and wish to mock it instead.

Although this is a very short function, 
writing the test code takes a lot of time. It's the fact that the function uses
a context manager makes the testing more complex than it should be.
*If you don't believe me, try to manually write mocks and asserts which verify
that `zip_container.writestr` was called with the right parameters.*

### Generating the 'Arrange' and 'Assert' sections using Mock Generator
To generate the 'Arrange' and 'Assert' sections, simply put this code at the beginning of 
your test function skeleton and run it (make sure to add the `mg` fixture):

```python
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker, mg):
    # arrange: todo  
    mg.generate_uut_mocks_with_asserts(process_and_zip)
    
    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # assert: todo
```
This will generate the sections for you:
```python
# mocked dependencies
mock_ZipFile = mocker.MagicMock(name='ZipFile')
mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
# calls to generate_asserts, put this after the 'act'
mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')
```
<b>The generated code is returned, printed to the console and also copied to the
clipboard for your convenience. 
Just paste it (as simple as ctrl+V) to your test function:</b>
```python
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker, mg):
    # arrange:  
    # mocked dependencies
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
    
    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # assert: todo
    # calls to generate_asserts, put this after the 'act'
    mg.generate_asserts(mock_ZipFile, name='mock_ZipFile')
```

Excellent! Arrange section is ready. Run the test function once more to get the asserts:
```python
assert 1 == mock_ZipFile.call_count
mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
mock_ZipFile.return_value.__enter__.assert_called_once_with()
mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)
```
Wow, that's a handful of asserts! Some are very useful: 
* Checking that we opened the zip file with the right parameters.
* Checking that we wrote the correct data to the proper file.
* Finally, ensuring that `__enter__` and `__exit__` are called, so there 
are no open file handles which could cause problems.

You can remove any generated lines which you find unnecessary.   

Paste that code right after the act phase, and you're done!

The complete test function:
```python
from tests.sample.code.tested_module import process_and_zip

def test_process_and_zip(mocker):
    # arrange:  
    # mocked dependencies
    mock_ZipFile = mocker.MagicMock(name='ZipFile')
    mocker.patch('tests.sample.code.tested_module.zipfile.ZipFile', new=mock_ZipFile)
    
    # act: invoking the tested code
    process_and_zip('/path/to.zip', 'in_zip.txt', 'foo bar')
    
    # assert:
    assert 1 == mock_ZipFile.call_count
    mock_ZipFile.assert_called_once_with('/path/to.zip', 'w')
    mock_ZipFile.return_value.__enter__.assert_called_once_with()
    mock_ZipFile.return_value.__enter__.return_value.writestr.assert_called_once_with('in_zip.txt', 'processed foo bar')
    mock_ZipFile.return_value.__exit__.assert_called_once_with(None, None, None)
```
Can you imagine the time it would have taken you to code this on your own?

### What's Next
#### Asserting Existing Mocks
At times, you may be editing a test function already containing mocks, or
you choose to write the mocks yourself, to gain some extra control.

Mock Generator can generate the assert section for standard 
Python mocks, even if they were not created using the Mock Generator. 

Put this after the 'Act' (replace `mock_obj` with your mock object name): 
```python
mg.generate_asserts(mock_obj)
```
Take the generated code and paste it at the 'Assert' section. 

## Troubleshooting
### No output is printed to the console when running Pytest
Be sure to run Pytest with appropriate flags to print the output: `pytest -rA`.

### No output is copied to the clipboard
Mock Generator uses [pyperclip](https://github.com/asweigart/pyperclip) for clipboard 
manipulations, look for errors / warnings printed to the console, similar to this one: 
```commandline
WARNING mock_autogen.utils:utils.py:28 
Could not copy func results to clipboard Traceback (most recent call last): 
    File "/home/username/Documents/code/test_mock_gen/.envtest/lib/python3.6/site-packages/mock_autogen/utils.py", line 25, in to_clipboard 
        pyperclip.copy(result) 
    File "/home/username/Documents/code/test_mock_gen/.envtest/lib/python3.6/site-packages/pyperclip/__init__.py", line 659, in lazy_load_stub_copy 
        return copy(text) 
    File "/home/username/Documents/code/test_mock_gen/.envtest/lib/python3.6/site-packages/pyperclip/__init__.py", line 336, in __call__
        raise PyperclipException(EXCEPT_MSG) pyperclip.PyperclipException: 
        
    Pyperclip could not find a copy/paste mechanism for your system. 
    For more information, please visit https://pyperclip.readthedocs.io/en/latest/index.html#not-implemented-error
```

It's possible that your system lacks some dependency, visit 
https://pyperclip.readthedocs.io/en/latest/index.html#not-implemented-error for 
additional troubleshooting steps.


## More information
Additional documentation can be found in the [mock-generator pypi](https://pypi.org/project/mock-generator).

## 📈 Releases

You can see the list of available releases on the [GitHub Releases](https://github.com/pksol/pytest-mock-generator/releases) page.

We follow [Semantic Versions](https://semver.org/) specification.

## 🛡 License

[![License](https://img.shields.io/github/license/pksol/pytest-mock-generator)](https://github.com/pksol/pytest-mock-generator/blob/master/LICENSE)

This project is licensed under the terms of the `MIT` license. See [LICENSE](https://github.com/pksol/pytest-mock-generator/blob/master/LICENSE) for more details.

## 📃 Citation

```bibtex
@misc{pytest-mock-generator,
  author = {Peter Kogan},
  title = {A pytest fixture wrapper for https://pypi.org/project/mock-generator},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  howpublished = {\url{https://github.com/pksol/pytest-mock-generator}}
}
```

## Credits [![🚀 Your next Python package needs a bleeding-edge project structure.](https://img.shields.io/badge/python--package--template-%F0%9F%9A%80-brightgreen)](https://github.com/TezRomacH/python-package-template)

This project was generated with [`python-package-template`](https://github.com/TezRomacH/python-package-template)
