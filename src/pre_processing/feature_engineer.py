"""Feature engineering"""
from sklearn.base import BaseEstimator,TransformerMixin
import pandas as pd

class FeatureCreator(BaseEstimator,TransformerMixin):
    def __init__(self,drop_origin = False):
        self.drop_origin = drop_origin
        self.EPSILON = 1e-6

    


