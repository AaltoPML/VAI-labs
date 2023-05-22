from sklearn.base import BaseEstimator
from vai_lab._plugin_templates import DataProcessingT
import pandas as pd
import numpy as np

_PLUGIN_READABLE_NAMES = {"ImgToFeatVect":"default",
                          "imgtofeatvect": "alias", 
                          "ImageToFeatureVector": "alias"}  # type:ignore
_PLUGIN_MODULE_OPTIONS = {"Type": "Other"}                  # type:ignore
_PLUGIN_REQUIRED_SETTINGS = {"Data": "str"}                 # type:ignore
_PLUGIN_OPTIONAL_SETTINGS = {}                              # type:ignore
_PLUGIN_REQUIRED_DATA = {}                                  # type:ignore
_PLUGIN_OPTIONAL_DATA = {"X","Y","X_tst","Y_tst"}           # type:ignore


class ImgToFeatVect(DataProcessingT):
    
    def __init__(self):
        """Initialises parent class. 
            Passes `globals` dict of all current variables
        """
        super().__init__(globals())
        self.proc = model()


class model(BaseEstimator):
    def __init__(self, optional=False):
        self.optional = optional
    
    def fit(self, X):
        """Defines the number of samples in the design, their placement
        and their size.
        
        Parameters
        ----------
        X : {dict}
            A dictionary containing images in each entry.
        Returns
        -------
        self : object
            Fitted model.
        """
        self.n = len(X.keys())
        h,w,self.rgb = next(iter(X.values())).shape
        self.d = h*w
        return self
    
    def transform(self, X):
        X_mat = np.dstack([X[el].reshape(self.d,self.rgb) for el in X.keys()])
        X_mat = X_mat.reshape(self.n,self.d,self.rgb)
        return pd.DataFrame(X_mat)
