import pandas
import os.path

FILES = ["effy2013",
         "hd2013",
         "ic2013_ay",
         "sfa1213"]

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ipeds_data/'))

rel_map = {-2: 'Not applicable',
 22: 'American Evangelical Lutheran Church',
 24: 'African Methodist Episcopal Zion Church',
 27: 'Assemblies of God Church',
 28: 'Brethren Church',
 30: 'Roman Catholic',
 33: 'Wisconsin Evangelical Lutheran Synod',
 34: 'Christ and Missionary Alliance Church',
 35: 'Christian Reformed Church',
 36: 'Evangelical Congregational Church',
 37: 'Evangelical Covenant Church of America',
 38: 'Evangelical Free Church of America',
 39: 'Evangelical Lutheran Church',
 40: 'International United Pentecostal Church',
 41: 'Free Will Baptist Church',
 42: 'Interdenominational',
 43: 'Mennonite Brethren Church',
 44: 'Moravian Church',
 45: 'North American Baptist',
 47: 'Pentecostal Holiness Church',
 48: 'Christian Churches and Churches of Christ',
 49: 'Reformed Church in America',
 50: 'Episcopal Church Reformed',
 51: 'African Methodist Episcopal',
 52: 'American Baptist',
 54: 'Baptist',
 55: 'Christian Methodist Episcopal',
 57: 'Church of God',
 58: 'Church of Brethren',
 59: 'Church of the Nazarene',
 60: 'Cumberland Presbyterian',
 61: 'Christian Church (Disciples of Christ)',
 64: 'Free Methodist',
 65: 'Friends',
 66: 'Presbyterian Church (USA)',
 67: 'Lutheran Church in America',
 68: 'Lutheran Church - Missouri Synod',
 69: 'Mennonite Church',
 71: 'United Methodist',
 73: 'Protestant Episcopal',
 74: 'Churches of Christ',
 75: 'Southern Baptist',
 76: 'United Church of Christ',
 77: 'Protestant not specified',
 78: 'Multiple Protestant Denomination',
 79: 'Other Protestant',
 80: 'Jewish',
 81: 'Reformed Presbyterian Church',
 84: 'United Brethren Church',
 87: 'Missionary Church Inc',
 88: 'Undenominational',
 89: 'Wesleyan',
 91: 'Greek Orthodox',
 92: 'Russian Orthodox',
 93: 'Unitarian Universalist',
 94: 'Latter Day Saints (Mormon Church)',
 95: 'Seventh Day Adventists',
 97: 'The Presbyterian Church in America',
 99: 'Other (none of the above)',
 100: 'Original Free Will Baptist',
 102: 'Evangelical Christian',
 103: 'Presbyterian'}

def get_names(data_name):
    fn = os.path.join(DATA_DIR, data_name)
    if os.path.exists(fn + ".xlsx"):
        return pandas.read_excel(fn + ".xlsx", sheetname=1).varTitle.tolist()
    elif os.path.exists(fn + ".xls"):
        return pandas.read_excel(fn + ".xls", sheetname=1).varTitle.tolist()
    else:
        raise Exception()

def get_inclusion(data_name):
    ext = None
    fn = os.path.join(DATA_DIR, data_name)
    if os.path.exists(fn + ".xlsx"):
        ext = ".xlsx"
    elif os.path.exists(fn + ".xls"):
        ext = ".xls"
    else:
        raise Exception()
    return pandas.read_excel(fn + ext, sheetname=1).varname.tolist()

def get_descriptions(data_name):
    ext = None
    fn = os.path.join(DATA_DIR, data_name)
    if os.path.exists(fn + ".xlsx"):
        ext = ".xlsx"
    elif os.path.exists(fn + ".xls"):
        ext = ".xls"
    else:
        raise Exception()
    return pandas.read_excel(fn + ext, sheetname=2)

def read_with_column_subset(data_name, subset):
    fn = os.path.join(DATA_DIR, data_name)
    header = get_names(data_name)
    include = get_inclusion(data_name)
    convert = { k:v for (k,v) in zip(include, header) }
    df = pandas.read_csv(fn + ".csv", index_col=0, usecols=(['UNITID'] + subset), na_values = [".", " ", "", "-2"])
    df.rename(columns=convert, inplace=True)
    return df

def get_descriptions_subset(data_name, subset):
    header = get_names(data_name)
    include = get_inclusion(data_name)
    convert = { k:v for (k,v) in zip(include, header) }
    desc_df = get_descriptions(data_name)
    desc_df = desc_df[ desc_df.varname.apply(lambda x: x in subset) ]
    desc_df.varname = desc_df.varname.apply(lambda x: convert[x])
    return desc_df


