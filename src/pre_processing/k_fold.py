"""
K-Fold: Tập Train được chia thành K=5. Giá trị mã hóa của một dòng chỉ được tính từ tỷ lệ 
rủi ro của 4 fold còn lại, chặn đứng rò rỉ nhãn cục bộ.
Smoothing: Cứu vớt các nhóm thiểu số có dữ liệu mỏng bằng cách kéo tỷ lệ 
vỡ nợ của chúng về gần tỷ lệ trung bình của toàn bộ dữ liệu.
"""

import pandas as pd

class KFoldTargetEncoder:
    def __init__(self,k:int,m:int):
        self.k = k
        self.m = m
    

    