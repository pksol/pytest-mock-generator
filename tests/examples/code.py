import os
import zipfile


def os_remove_wrap(filename):
    os.remove(filename)


def process_and_zip(zip_path, file_name, contents):
    processed_contents = "processed " + contents  # some complex logic
    with zipfile.ZipFile(zip_path, "w") as zip_container:
        zip_container.writestr(file_name, processed_contents)
