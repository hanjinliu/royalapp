from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from royalapp.io import register_writer_provider
from royalapp.types import WidgetDataModel
from royalapp.consts import StandardTypes, BasicTextFileTypes, ConventionalTextFileNames
from royalapp import register_reader_provider

if TYPE_CHECKING:
    import numpy as np


def _read_text(file_path: Path) -> WidgetDataModel:
    """Read text file."""
    with open(file_path) as f:
        return WidgetDataModel(
            value=f.read(),
            type=StandardTypes.TEXT,
            source=Path(file_path),
        )


def _read_simple_image(file_path: Path) -> WidgetDataModel:
    """Read image file."""
    import numpy as np
    from PIL import Image

    arr = np.array(Image.open(file_path))

    return WidgetDataModel(
        value=arr,
        type=StandardTypes.IMAGE,
    )


def _read_csv(file_path: Path) -> WidgetDataModel:
    """Read CSV file."""
    import csv

    with open(file_path) as f:
        reader = csv.reader(f)
        data = list(reader)

    return WidgetDataModel(
        value=data,
        type=StandardTypes.TABLE,
    )


def _read_tsv(file_path: Path) -> WidgetDataModel:
    """Read TSV file."""
    import csv

    with open(file_path) as f:
        reader = csv.reader(f, delimiter="\t")
        data = list(reader)

    return WidgetDataModel(
        value=data,
        type=StandardTypes.TABLE,
    )


@register_reader_provider
def default_reader_provider(file_path: Path | list[Path]):
    """Get default reader."""
    if isinstance(file_path, list):
        return None
    if file_path.suffix in BasicTextFileTypes:
        return _read_text
    elif file_path.suffix == ".csv":
        return _read_csv
    elif file_path.suffix == ".tsv":
        return _read_tsv
    elif file_path.suffix in {".png", ".jpg", ".jpeg"}:
        return _read_simple_image
    elif file_path.name in ConventionalTextFileNames:
        return _read_text
    return None


def _write_text(model: WidgetDataModel[str], path: Path) -> None:
    """Write text file."""
    with open(path, "w") as f:
        f.write(model.value)
    return None


def _write_csv(model: WidgetDataModel[list[list[str]]], path: Path) -> None:
    """Write CSV file."""
    import csv

    with open(path, "w") as f:
        writer = csv.writer(f)
        writer.writerows(model.value)


def _write_image(model: WidgetDataModel[np.ndarray], path: Path) -> None:
    """Write image file."""
    from PIL import Image

    Image.fromarray(model.value).save(path)
    return None


@register_writer_provider
def default_writer_provider(model: WidgetDataModel):
    """Get default writer."""
    if model.type is None:
        return None
    if model.is_subtype_of(StandardTypes.TEXT):
        return _write_text
    elif model.is_subtype_of(StandardTypes.TABLE):
        return _write_csv
    elif model.is_subtype_of(StandardTypes.IMAGE):
        return _write_image
    else:
        return None
