import numpy as np
from scipy import ndimage as ndi
from typing import Annotated

from royalapp import new_window
from royalapp.plugins import get_plugin_interface
from royalapp.types import WidgetDataModel, Parametric
from royalapp.consts import StandardTypes

interf = get_plugin_interface()

@interf.register_function(title="Gaussian Filter", types=StandardTypes.IMAGE)
def gaussian_filter(model: WidgetDataModel[np.ndarray]) -> Parametric:
    def func(sigma: float = 1.0) -> WidgetDataModel[np.ndarray]:
        im = model.value
        if im.ndim == 3:
            im = ndi.gaussian_filter(im, sigma=sigma, axes=(0, 1))
        else:
            im = ndi.gaussian_filter(im, sigma=sigma)
        return WidgetDataModel(
            value=im,
            type=StandardTypes.IMAGE,
            title=model.title + "-Gaussian",
        )
    return func

@interf.register_function(title="Add", types=StandardTypes.IMAGE)
def add_images() -> Parametric:
    def func(
        a: Annotated[WidgetDataModel[np.ndarray], {"types": StandardTypes.IMAGE}],
        b: Annotated[WidgetDataModel[np.ndarray], {"types": StandardTypes.IMAGE}],
    ) -> WidgetDataModel[np.ndarray]:
        return WidgetDataModel(
            value=a.value + b.value,
            type=StandardTypes.IMAGE,
            title="result",
        )
    return func

def main():
    ui = new_window(plugins=[interf])
    im = np.random.default_rng(123).normal(size=(100, 100))
    ui.add_data(im, type=StandardTypes.IMAGE, title="Noise")
    ui.show(run=True)

if __name__ == "__main__":
    main()
