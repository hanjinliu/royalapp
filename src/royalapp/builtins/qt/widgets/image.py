from __future__ import annotations

from typing import TYPE_CHECKING
from qtpy import QtWidgets as QtW
from qtpy import QtGui, QtCore
from superqt import QLabeledSlider
from royalapp.consts import StandardTypes
from royalapp.types import WidgetDataModel

if TYPE_CHECKING:
    import numpy as np
    from numpy.typing import NDArray


class _QImageLabel(QtW.QLabel):
    def __init__(self, val):
        super().__init__()
        self._transformation = QtCore.Qt.TransformationMode.SmoothTransformation
        self.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(
            QtW.QSizePolicy.Policy.Expanding, QtW.QSizePolicy.Policy.Expanding
        )
        self.set_array(val)

    def set_array(self, val: NDArray[np.uint8]):
        import numpy as np

        if val.ndim == 2:
            val = np.stack(
                [val] * 3 + [np.full(val.shape, 255, dtype=np.uint8)], axis=2
            )
        image = QtGui.QImage(
            val, val.shape[1], val.shape[0], QtGui.QImage.Format.Format_RGBA8888
        )
        self._pixmap_orig = QtGui.QPixmap.fromImage(image)
        self._update_pixmap()

    def _update_pixmap(self):
        sz = self.size()
        self.setPixmap(
            self._pixmap_orig.scaled(
                sz,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                self._transformation,
            )
        )

    def resizeEvent(self, ev: QtGui.QResizeEvent) -> None:
        self._update_pixmap()


class QDefaultImageView(QtW.QWidget):
    def __init__(self, model: WidgetDataModel[NDArray[np.uint8]]):
        import numpy as np

        super().__init__()
        layout = QtW.QVBoxLayout(self)
        arr = np.asarray(model.value)
        ndim = arr.ndim - 2
        if arr.shape[-1] in (3, 4):
            ndim -= 1
        sl_0 = (0,) * ndim
        self._image_label = _QImageLabel(self.as_image_array(arr[sl_0]))
        layout.addWidget(self._image_label)

        self._sliders: list[QtW.QSlider] = []
        for i in range(ndim):
            slider = QLabeledSlider(QtCore.Qt.Orientation.Horizontal)
            self._sliders.append(slider)
            layout.addWidget(slider, alignment=QtCore.Qt.AlignmentFlag.AlignBottom)
            slider.setRange(0, model.value.shape[i] - 1)
            slider.valueChanged.connect(self._slider_changed)

        self._interpolation_check_box = QtW.QCheckBox()
        self._interpolation_check_box.setText("smooth")
        self._interpolation_check_box.setChecked(True)
        self._interpolation_check_box.stateChanged.connect(self._interpolation_changed)
        layout.addWidget(self._interpolation_check_box)
        self._arr = arr

    def _slider_changed(self):
        sl = tuple(sl.value() for sl in self._sliders)
        arr = self.as_image_array(self._arr[sl])
        self._image_label.set_array(arr)

    def _interpolation_changed(self, checked: bool):
        if checked:
            tr = QtCore.Qt.TransformationMode.SmoothTransformation
        else:
            tr = QtCore.Qt.TransformationMode.FastTransformation
        self._image_label._transformation = tr
        self._image_label._update_pixmap()

    @classmethod
    def from_model(cls, model: WidgetDataModel) -> QDefaultImageView:
        self = cls(model)
        if model.source is not None:
            self.setObjectName(model.source.name)
        return self

    def to_model(self) -> WidgetDataModel[NDArray[np.uint8]]:
        return WidgetDataModel(
            value=self._arr,
            type=self.model_type(),
            extension_default=".png",
        )

    def model_type(self) -> str:
        return StandardTypes.IMAGE

    def size_hint(self) -> tuple[int, int]:
        return 400, 400

    def as_image_array(self, arr: np.ndarray) -> NDArray[np.uint8]:
        import numpy as np

        if arr.dtype == "uint8":
            arr0 = arr
        elif arr.dtype == "uint16":
            arr0 = (arr / 256).astype("uint8")
        elif arr.dtype.kind == "f":
            min_ = arr.min()
            max_ = arr.max()
            if min_ < max_:
                arr0 = ((arr - min_) / (max_ - min_) * 255).astype("uint8")
            else:
                arr0 = np.zeros(arr.shape, dtype=np.uint8)
        else:
            raise ValueError(f"Unsupported data type: {arr.dtype}")
        return np.ascontiguousarray(arr0)
