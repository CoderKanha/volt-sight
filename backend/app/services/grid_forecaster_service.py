"""
Loader for the new team's GridForecaster bundle.

The handoff estimators were serialized with scikit-learn 1.6.1.
VoltSight's existing model was serialized in its newer dependency environment.
We keep one shared dependency set (the existing backend lock) and apply a
narrow SimpleImputer state compatibility shim for the handoff estimator.
"""
"""
from functools import lru_cache
import warnings

from sklearn.impute import SimpleImputer
import sys

import sklearn._loss._loss as sklearn_loss_extension

# Compatibility for models serialized with the old private module path.
sys.modules.setdefault("_loss", sklearn_loss_extension)

# sklearn 1.8+ expects SimpleImputer._fill_dtype during transform, while
# the supplied sklearn 1.6.1 pickle stores _fit_dtype. Map the old state
# to the newer attribute during unpickling.
_original_setstate = getattr(SimpleImputer, "__setstate__", None)

def _simple_imputer_compat_setstate(self, state):
    if _original_setstate is not None:
        _original_setstate(self, state)
    else:
        self.__dict__.update(state)

    if not hasattr(self, "_fill_dtype") and hasattr(self, "_fit_dtype"):
        self._fill_dtype = self._fit_dtype

SimpleImputer.__setstate__ = _simple_imputer_compat_setstate

from app.model_bundle.src.grid_forecaster import GridForecaster
from pathlib import Path

BUNDLE_DIR = Path(__file__).resolve().parents[1] / "model_bundle"

@lru_cache(maxsize=1)
def get_grid_forecaster():
    # The bundle is trusted and shipped with this application.
    # Suppress only the expected cross-version warning after applying the
    # narrowly scoped compatibility mapping; other warnings remain visible.
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Trying to unpickle estimator .* from version 1\\.6\\.1",
            category=UserWarning,
        )
        return GridForecaster(BUNDLE_DIR)
 """


"""
Loader for the new team's GridForecaster bundle.

The handoff estimators were serialized with scikit-learn 1.6.1.
VoltSight uses a shared, newer dependency environment.

Compatibility adjustments:
1. Map the old private '_loss' module path to sklearn's loss extension.
2. Map the old SimpleImputer '_fit_dtype' state to '_fill_dtype'.
"""

import sys
import warnings
from functools import lru_cache
from pathlib import Path

import sklearn._loss._loss as sklearn_loss_extension
from sklearn.impute import SimpleImputer

from app.model_bundle.src.grid_forecaster import GridForecaster


# ---------------------------------------------------------
# 1. Compatibility for the old '_loss' pickle module path
# ---------------------------------------------------------

sys.modules.setdefault("_loss", sklearn_loss_extension)


# ---------------------------------------------------------
# 2. SimpleImputer state compatibility
# ---------------------------------------------------------

if not getattr(SimpleImputer, "_voltsight_compat_patched", False):

    _original_setstate = getattr(SimpleImputer, "__setstate__", None)

    def _simple_imputer_compat_setstate(self, state):

        if _original_setstate is not None:
            _original_setstate(self, state)
        else:
            self.__dict__.update(state)

        # Compatibility with estimators serialized using older sklearn.
        if (
            not hasattr(self, "_fill_dtype")
            and hasattr(self, "_fit_dtype")
        ):
            self._fill_dtype = self._fit_dtype

    SimpleImputer.__setstate__ = _simple_imputer_compat_setstate

    SimpleImputer._voltsight_compat_patched = True


# ---------------------------------------------------------
# 3. Model bundle directory
# ---------------------------------------------------------

BUNDLE_DIR = Path(__file__).resolve().parents[1] / "model_bundle"


# ---------------------------------------------------------
# 4. Cached GridForecaster instance
# ---------------------------------------------------------

@lru_cache(maxsize=1)
def get_grid_forecaster():

    with warnings.catch_warnings():

        warnings.filterwarnings(
            "ignore",
            message=r"Trying to unpickle estimator .* from version 1\.6\.1",
            category=UserWarning,
        )

        return GridForecaster(BUNDLE_DIR)
