from pathlib import Path


def get_path(path):
    """Get the `path` under the `examples/` directory, with respect to this file."""
    root = Path(__file__).parent
    examples = "./examples"
    if root.joinpath(examples).exists():
        examples = root.joinpath(examples)
    else:
        while root.joinpath("..").exists():
            root = root.joinpath("..")
            if root.joinpath(examples).exists():
                examples = root.joinpath(examples)
                break
        else:
            raise FileNotFoundError("examples/ directory cannot be found")

    return examples.joinpath(path).resolve()


def document_path():
    """Get the path for the `document.html` example file."""
    return get_path("document.html")


def table_path():
    """Get the path for the `table.html` example file."""
    return get_path("table.html")
