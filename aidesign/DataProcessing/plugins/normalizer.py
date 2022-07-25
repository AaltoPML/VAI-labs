from sklearn.preprocessing import Normalizer as model
import numpy as np
import pandas as pd

_PLUGIN_READABLE_NAMES = {"Normalizer":"default","Norm":"alias","normalizer":"alias"}
_PLUGIN_MODULE_OPTIONS = {"Type": "scaler"}
_PLUGIN_REQUIRED_SETTINGS = {"Data": "str"}
_PLUGIN_OPTIONAL_SETTINGS = {"norm": "str"}
_PLUGIN_REQUIRED_DATA = {}
_PLUGIN_OPTIONAL_DATA = {"X","Y","X_tst", 'Y_tst'}

class Normalizer(object):
    """
    Normalize samples individually to unit norm
    """

    def __init__(self):
        self.X = None
        self.Y = None
        self.X_tst = None
        self.Y_tst = None
        self.proc = model()

    def set_data_in(self,data_in):
        req_check = [r for r in _PLUGIN_REQUIRED_DATA if r not in data_in.keys()]
        if len(req_check) > 0:
            raise Exception("Minimal Data Requirements not met"   \
                            +"\n\t{0} ".format(Normalizer) \
                            +"requires data: {0}".format(_PLUGIN_REQUIRED_DATA)\
                            + "\n\tThe following data is missing:"\
                            + "\n\t\u2022 {}".format(",\n\t\u2022 ".join([*req_check])))
        self._data_in = data_in

    def configure(self, config:dict):
        self._config = config
        self._parse_config()

    def _parse_config(self):
        if self._config["options"]["Data"] == 'X':
            self.X  = self._data_in["X"]
            self.X_tst = self._is_name_passed(self._data_in, "X_test")
        elif self._config["options"]["Data"] == 'Y':
            self.X  = self._data_in["Y"]
            self.X_tst = self._is_name_passed(self._data_in, "Y_test")
        else:
            print('Invalid Data name. Indicate whether to use `X` or `Y`')

    def _is_name_passed(self, dic: dict, key: str, default = None):
        return dic[key] if key in dic.keys() and dic[key] is not None else default

    def _reshape(self,data,shape):
        return data.reshape(shape[0],shape[1])

    def _check_numeric(self, dict_opt):
        new_dict = {}
        for key, val in dict_opt.items():
            """ 
            TODO: Maybe, if list -> cv
            """
            if key != 'Data':
                if type(val) == str and val.replace('.','').replace(',','').isnumeric():
                    val = float(val)
                    if val.is_integer():
                        val = int(val)
                new_dict[key] = val
        return new_dict

    def fit(self):
        config = self._check_numeric(self._config["options"])
        self.proc.set_params(**config)
        self.proc.fit(self.X)

    def transform(self,data):
        data.append_data_column("X", pd.DataFrame(self.proc.transform(self.X)))
        if self.X_tst is not None:
            data.append_data_column("X_test", pd.DataFrame(self.proc.transform(self.X_tst)))
        return data