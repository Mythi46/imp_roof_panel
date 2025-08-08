
class DevGen:
    # DataFrame Constants
    DataFrameNone = 0
    DataFrameStart = 1
    DataFrameEnd = 2
    DataNotNeeded = 3

    # DataLabel Constants
    DataLabelNone = 0
    DataLabelGoodTeach = 1
    DataLabelGoodInference = 2
    DataLabelBadTeach = 3
    DataLabelBadInference = 4

    DataCiteMade = 1 # 手作り
    DataCiteAct  = 2 # 実データ
    DataCiteGen  = 3 # 生成データ
    DataCiteFil  = 4 # 歯抜け補填データ