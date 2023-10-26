from vai_lab._plugin_templates import DataProcessingT

import pandas as pd
from sklearn.preprocessing import KBinsDiscretizer as model

_PLUGIN_READABLE_NAMES = {"KBinsDiscretizer":"default"} # type:ignore
_PLUGIN_MODULE_OPTIONS = {"Type": "encoder"}            # type:ignore
_PLUGIN_REQUIRED_SETTINGS = {}                          # type:ignore
_PLUGIN_OPTIONAL_SETTINGS = {}                          # type:ignore
_PLUGIN_REQUIRED_DATA = {}                              # type:ignore
_PLUGIN_OPTIONAL_DATA = {"X","Y","X_tst","Y_tst"}       # type:ignore

class KBinsDiscretizer(DataProcessingT):
    """
    Bin continuous data into interval
    """

    def __init__(self, config = {}, data_in = [None]):
        """Initialises parent class. 
            Passes `globals` dict of all current variables
        """
        super().__init__(globals())
        self.set_data_in(data_in)
        self.configure(config)
        
        try:
            self.model = model(**self._config["options"])
        except Exception as exc:
            print('The plugin encountered an error on the parameters of '
                     +str(list(self._PLUGIN_READABLE_NAMES.keys())[list(self._PLUGIN_READABLE_NAMES.values()).index('default')])+': '+str(exc)+'.')
            raise
        
        self.fit_plugin = self.model.fit
        self.transform_plugin = self.model.transform