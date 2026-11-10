
import asyncio
import os
import subprocess
import aiofiles

import numpy as np
import sklearn.preprocessing
import sklearn
import configparser
import math
import os
import re
import shutil
from queue import Queue
from threading import Lock



RACs = ['D_func-I-0-all','D_func-I-1-all','D_func-I-2-all','D_func-I-3-all',
 'D_func-S-0-all', 'D_func-S-1-all', 'D_func-S-2-all', 'D_func-S-3-all',
 'D_func-T-0-all', 'D_func-T-1-all', 'D_func-T-2-all', 'D_func-T-3-all',
 'D_func-Z-0-all', 'D_func-Z-1-all', 'D_func-Z-2-all', 'D_func-Z-3-all',
 'D_func-chi-0-all', 'D_func-chi-1-all', 'D_func-chi-2-all',
 'D_func-chi-3-all', 'D_lc-I-0-all', 'D_lc-I-1-all', 'D_lc-I-2-all',
 'D_lc-I-3-all', 'D_lc-S-0-all', 'D_lc-S-1-all', 'D_lc-S-2-all',
 'D_lc-S-3-all', 'D_lc-T-0-all', 'D_lc-T-1-all', 'D_lc-T-2-all',
 'D_lc-T-3-all', 'D_lc-Z-0-all', 'D_lc-Z-1-all', 'D_lc-Z-2-all',
 'D_lc-Z-3-all', 'D_lc-chi-0-all', 'D_lc-chi-1-all', 'D_lc-chi-2-all',
 'D_lc-chi-3-all', 'D_mc-I-0-all', 'D_mc-I-1-all', 'D_mc-I-2-all',
 'D_mc-I-3-all', 'D_mc-S-0-all', 'D_mc-S-1-all', 'D_mc-S-2-all',
 'D_mc-S-3-all', 'D_mc-T-0-all', 'D_mc-T-1-all', 'D_mc-T-2-all',
 'D_mc-T-3-all', 'D_mc-Z-0-all', 'D_mc-Z-1-all', 'D_mc-Z-2-all',
 'D_mc-Z-3-all', 'D_mc-chi-0-all', 'D_mc-chi-1-all', 'D_mc-chi-2-all',
 'D_mc-chi-3-all', 'f-I-0-all', 'f-I-1-all', 'f-I-2-all', 'f-I-3-all',
 'f-S-0-all', 'f-S-1-all', 'f-S-2-all', 'f-S-3-all', 'f-T-0-all', 'f-T-1-all',
 'f-T-2-all', 'f-T-3-all', 'f-Z-0-all', 'f-Z-1-all', 'f-Z-2-all', 'f-Z-3-all',
 'f-chi-0-all', 'f-chi-1-all', 'f-chi-2-all', 'f-chi-3-all', 'f-lig-I-0',
 'f-lig-I-1', 'f-lig-I-2', 'f-lig-I-3', 'f-lig-S-0', 'f-lig-S-1', 'f-lig-S-2',
 'f-lig-S-3', 'f-lig-T-0', 'f-lig-T-1', 'f-lig-T-2', 'f-lig-T-3', 'f-lig-Z-0',
 'f-lig-Z-1', 'f-lig-Z-2', 'f-lig-Z-3', 'f-lig-chi-0', 'f-lig-chi-1',
 'f-lig-chi-2', 'f-lig-chi-3', 'func-I-0-all', 'func-I-1-all',
 'func-I-2-all', 'func-I-3-all', 'func-S-0-all', 'func-S-1-all',
 'func-S-2-all', 'func-S-3-all', 'func-T-0-all', 'func-T-1-all',
 'func-T-2-all', 'func-T-3-all', 'func-Z-0-all', 'func-Z-1-all',
 'func-Z-2-all', 'func-Z-3-all', 'func-chi-0-all', 'func-chi-1-all',
 'func-chi-2-all', 'func-chi-3-all', 'lc-I-0-all', 'lc-I-1-all', 'lc-I-2-all',
 'lc-I-3-all', 'lc-S-0-all', 'lc-S-1-all', 'lc-S-2-all', 'lc-S-3-all',
 'lc-T-0-all', 'lc-T-1-all', 'lc-T-2-all', 'lc-T-3-all', 'lc-Z-0-all',
 'lc-Z-1-all', 'lc-Z-2-all', 'lc-Z-3-all', 'lc-chi-0-all', 'lc-chi-1-all',
 'lc-chi-2-all', 'lc-chi-3-all', 'mc-I-0-all', 'mc-I-1-all', 'mc-I-2-all',
 'mc-I-3-all', 'mc-S-0-all', 'mc-S-1-all', 'mc-S-2-all', 'mc-S-3-all',
 'mc-T-0-all', 'mc-T-1-all', 'mc-T-2-all', 'mc-T-3-all', 'mc-Z-0-all',
 'mc-Z-1-all', 'mc-Z-2-all', 'mc-Z-3-all', 'mc-chi-0-all', 'mc-chi-1-all',
 'mc-chi-2-all', 'mc-chi-3-all']
geo = ['Df','Di', 'Dif','GPOAV','GPONAV','GPOV','GSA','POAV','POAV_vol_frac',
  'PONAV','PONAV_vol_frac','VPOV','VSA','rho']

def solvent_normalize_data(df_train, df_test, fnames, lname, unit_trans=1, debug=False):
    _df_train = df_train.copy().dropna(subset=fnames+lname)
    _df_test = df_test.copy().dropna(subset=fnames+lname)
    X_train, X_test = _df_train[fnames].values, _df_test[fnames].values
    y_train, y_test = _df_train[lname].values, _df_test[lname].values
    if debug:
        print("training data reduced from %d -> %d because of nan." % (len(df_train), y_train.shape[0]))
        print("test data reduced from %d -> %d because of nan." % (len(df_test), y_test.shape[0]))
    x_scaler = sklearn.preprocessing.StandardScaler()
    x_scaler.fit(X_train)
    X_train = x_scaler.transform(X_train)
    X_test = x_scaler.transform(X_test)
    y_train = np.array([1 if x == 1 else 0 for x in y_train.reshape(-1, )])
    y_test = np.array([1 if x == 1 else 0 for x in y_test.reshape(-1, )])
    return X_train, X_test, y_train, y_test, x_scaler

def thermal_normalize_data(df_train, df_test, fnames, lname, unit_trans=1, debug=False):
    _df_train = df_train.copy().dropna(subset=fnames+lname)
    _df_test = df_test.copy().dropna(subset=fnames+lname)
    X_train, X_test = _df_train[fnames].values, _df_test[fnames].values
    y_train, y_test = _df_train[lname].values, _df_test[lname].values
    if debug:
        print("training data reduced from %d -> %d because of nan." % (len(df_train), y_train.shape[0]))
        print("test data reduced from %d -> %d because of nan." % (len(df_test), y_test.shape[0]))
    x_scaler = sklearn.preprocessing.StandardScaler()
    x_scaler.fit(X_train)
    X_train = x_scaler.transform(X_train)
    X_test = x_scaler.transform(X_test)
    y_scaler = sklearn.preprocessing.StandardScaler()
    y_scaler.fit(y_train)
    y_train = y_scaler.transform(y_train)
    y_test = y_scaler.transform(y_test)
    return X_train, X_test, y_train, y_test, x_scaler, y_scaler

def standard_labels(df, key="flag"):
    flags = [1 if row[key] == 1 else 0 for _, row in df.iterrows()]
    df[key] = flags
    return df

def precision(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    predicted_positives = K.sum(K.round(K.clip(y_pred, 0, 1)))
    precision = true_positives / (predicted_positives + K.epsilon())
    return precision

def recall(y_true, y_pred):
    true_positives = K.sum(K.round(K.clip(y_true * y_pred, 0, 1)))
    possible_positives = K.sum(K.round(K.clip(y_true, 0, 1)))
    recall = true_positives / (possible_positives + K.epsilon())
    return recall

def f1(y_true, y_pred):
    p = precision(y_true, y_pred)
    r = recall(y_true, y_pred)
    return 2 * ((p * r) / (p + r + K.epsilon()))

class RASPA_Output_Data():
    '''
        RASPA output file object
    '''
    '''
    demo:
        with open('./output.data','r') as f:
            str = f.read()
        output = RASPA_Output_Data(str)
        print(output.is_finished())
        print(output.get_absolute_adsorption())

    '''

    def __init__(self, output_string):
        '''
            The string passed into the RASPA output file during initialization
        '''
        self.output_string = output_string
        self.components = re.findall(
            r'Component \d+ \[(.*)\] \(Adsorbate molecule\)', self.output_string)

    def get_components(self):
        return self.components

    def is_finished(self):
        '''
            Returns whether the task has been completed
        '''
        pattern = r'Simulation finished'
        result = re.findall(pattern, self.output_string)
        return len(result) > 0

    def get_warnings(self):
        '''
            Returns a list of stored warning messages
        '''
        if len(re.findall(r'0 warnings', self.output_string)) > 0:
            return []
        pattern = r'WARNING: (.*)\n'
        return list(set(re.findall(pattern, self.output_string)))

    def get_pressure(self):
        '''
            Return pressure, unit is Pa
        '''
        pattern = r'Pressure:\s+(.*)\s+\[Pa\]'
        result = re.findall(pattern, self.output_string)
        return result[0]

    def get_excess_adsorption(self, unit='cm^3/g'):
        '''
            Specify the unit and return the excess adsorption amount. The return value is a dictionary, the key is the name of the adsorbate, and the value is the adsorption amount. 
            If the unit is not specified, the default is cm^3/g.
            unit: 'mol/uc','cm^3/g','mol/kg','mg/g','cm^3/cm^3'
        '''
        patterns = {'mol/uc': r"Average loading excess \[molecules/unit cell\]\s+(-?\d+\.?\d*)\s+",
                    'cm^3/g': r"Average loading excess \[cm\^3 \(STP\)/gr framework\]\s+(-?\d+\.?\d*)\s+",
                    'mol/kg': r"Average loading excess \[mol/kg framework\]\s+(-?\d+\.?\d*)\s+",
                    'mg/g': r"Average loading excess \[milligram/gram framework\]\s+(-?\d+\.?\d*)\s+",
                    'cm^3/cm^3': r"Average loading excess \[cm\^3 \(STP\)/cm\^3 framework\]\s+(-?\d+\.?\d*)\s+"
                    }
        if unit not in patterns.keys():
            raise ValueError('Wrong unit!')
        result = {}
        data = re.findall(patterns[unit], self.output_string)
        for i, j in zip(self.components, data):
            result[i] = j
        return result

    def get_absolute_adsorption(self, unit='cm^3/g'):
        '''
            Specify the unit and return the absolute adsorption amount. The return value is a dictionary, the key is the name of the adsorbate, and the value is the adsorption amount;
            If the unit is not specified, the default is cm^3/g
            unit: 'mol/uc','cm^3/g','mol/kg','mg/g','cm^3/cm^3'
        '''
        patterns = {'mol/uc': r"Average loading absolute \[molecules/unit cell\]\s+(-?\d+\.?\d*)\s+",
                    'cm^3/g': r"Average loading absolute \[cm\^3 \(STP\)/gr framework\]\s+(-?\d+\.?\d*)\s+",
                    'mol/kg': r"Average loading absolute \[mol/kg framework\]\s+(-?\d+\.?\d*)\s+",
                    'mg/g': r"Average loading absolute \[milligram/gram framework\]\s+(-?\d+\.?\d*)\s+",
                    'cm^3/cm^3': r"Average loading absolute \[cm\^3 \(STP\)/cm\^3 framework\]\s+(-?\d+\.?\d*)\s+"
                    }
        if unit not in patterns.keys():
            raise ValueError('Wrong unit!')
        result = {}
        data = re.findall(patterns[unit], self.output_string)
        for i, j in zip(self.components, data):
            result[i] = j
        return result


def get_unit_cell(cif_location, cutoff):
    with open(cif_location, 'r') as f:
        text = f.readlines()
    for i in text:
        if (i.startswith('_cell_length_a')):
            a = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_length_b')):
            b = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_length_c')):
            c = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_alpha')):
            alpha = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_beta')):
            beta = float(i.split()[-1].strip().split('(')[0])
        elif (i.startswith('_cell_angle_gamma')):
            gamma = float(i.split()[-1].strip().split('(')[0])
            break
    pi = 3.1415926

    a_length = a * math.sin(beta / 180 * pi)
    b_length = b * math.sin(gamma / 180 * pi)
    c_length = c * math.sin(alpha / 180 * pi)

    a_unitcell = int(2 * cutoff / a_length + 1)
    b_unitcell = int(2 * cutoff / b_length + 1)
    c_unitcell = int(2 * cutoff / c_length + 1)

    return "{} {} {}".format(a_unitcell, b_unitcell, c_unitcell)


def generate_simulation_input(template: str, cutoff: float, cif_file_path: str):
    # 提取不包含扩展名的文件名
    cif_name = os.path.basename(cif_file_path).replace('.cif', '')
    # 假设 get_unit_cell 函数返回你需要插入模板的 "UnitCells" 值
    unitcell = get_unit_cell(cif_file_path, cutoff)
    # 使用 format 方法替换模板中的占位符
    return template.format(cif_name=cif_name, cutoff=cutoff, unitcell=unitcell)


def work(cif_file_path: str, RASPA_dir: str, result_file: str, components: list, headers: list, input_text: str):
    cif_name = os.path.basename(cif_file_path).replace('.cif', '')
    output_dir = "/home/hjj/project/ToolsKG/TempFiles/RASPA_Output"
    cmd_dir = os.path.join(output_dir, cif_name)
    if not os.path.exists(cmd_dir):
        os.makedirs(cmd_dir)
    
    # 将 CIF 文件复制到命令目录
    shutil.copy(cif_file_path, cmd_dir)
    
    # 在 cmd_dir 下创建 simulation.input 文件
    simulation_input_path = os.path.join(cmd_dir, "simulation.input")
    with open(simulation_input_path, "w") as f1:
        f1.write(input_text)
    
    # 构建 RASPA 运行命令
    cmd = [os.path.join(RASPA_dir, "bin", "simulate"), "simulation.input"]
    # print(f"Running command: {' '.join(cmd)}")
    # 切换到命令目录
    os.chdir(cmd_dir)
    print(f"Running command in {cmd_dir}: {' '.join(cmd)}")

    try:
        # 使用 subprocess 执行命令
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print(result.stdout)
        
        # 处理 RASPA 输出文件
        output_file = os.listdir(os.path.join(cmd_dir, "Output", "System_0"))[0]
        with open(os.path.join(cmd_dir, "Output", "System_0", output_file), 'r') as f2:
            result = get_result(f2.read(), components, cif_name)
        write_result(result_file, result, headers)
        print(f"\033[0;30;42m\n{cif_name} has completed\n\033[0m")
    except subprocess.CalledProcessError as e:
        # 写入错误结果
        write_error(result_file, cif_name)
        print(f"\033[0;37;41m\n{cif_name} error: {e}!\n\033[0m")
    except Exception as e:
        # 处理其他异常
        print(f"\033[0;37;41m\nUnexpected error: {repr(e)} !\n\033[0m")
            
def get_result(output_str: str, components: list, cif_name: str):
    res = {}
    units = ['mol/uc', 'cm^3/g', 'mol/kg', 'mg/g', 'cm^3/cm^3']
    res["filename"] = cif_name + '.cif'
    output = RASPA_Output_Data(output_str)
    res["finished"] = str(output.is_finished())
    res["warning"] = ""
    if res["finished"] == 'True':
        for w in output.get_warnings():
            res["warning"] += (w + "; ")

        for unit in units:
            absolute_capacity = output.get_absolute_adsorption(unit=unit)
            excess_capacity = output.get_excess_adsorption(unit=unit)
            for c in components:
                res[c + "_absolute_" + unit] = absolute_capacity[c]
                res[c + "_excess_" + unit] = excess_capacity[c]
    else:
        for unit in units:
            for c in components:
                res[c + "_absolute_" + unit] = " "
                res[c + "_excess_" + unit] = " "
    return res


def get_field_headers(components: list):
    headers = ["filename", "finished"]
    units = ['mol/uc', 'cm^3/g', 'mol/kg', 'mg/g', 'cm^3/cm^3']
    for i in ["absolute", "excess"]:
        for j in components:
            for unit in units:
                headers.append(j + "_" + i + "_" + unit)
    headers.append("warning")
    return headers


def get_components_from_input(input_text: str):
    components = re.findall(r'MoleculeName\s+(.+)', input_text)
    return components


def write_result(result_file, result: dict, headers: list):
    with open(result_file, 'a') as f:
        for i in range(len(headers)):
            if i != len(headers) - 1:
                f.write(result[headers[i]] + ",")
            else:
                f.write(result[headers[i]] + "\n")
        f.close()


def write_error(result_file, cif_name):
    with open(result_file, 'a') as f:
        f.write(cif_name + ",Error,\n")
        f.close()

async def awrite_result(result_file, result: dict, headers: list):
    async with aiofiles.open(result_file, 'a') as f:
        for i in range(len(headers)):
            if i != len(headers) - 1:
                await f.write(result[headers[i]] + ",")
            else:
                await f.write(result[headers[i]] + "\n")

async def awrite_error(result_file, cif_name):
    async with aiofiles.open(result_file, 'a') as f:
        await f.write(cif_name + ",Error,\n")


def check_parameters(cif_file_path):
    base_path = "/home/hjj/project/"
    config_path = os.path.join(base_path, "ToolsKG/ToolsFuns/Material/utils/config.ini")

    config = configparser.ConfigParser()
    config.read(config_path, encoding='utf8')
    section = "ADSORPTION_CONFIG"
    
    options_in_config = config.options(section)
    missing_options = []
    option_dic = {}
    full_options = ['raspa_dir', 'cutoffvdm', 'max_threads']
    
    for op in full_options:
        if op not in options_in_config:
            missing_options.append(op)
        else:
            option_dic[op] = config.get(section, op)

    if len(missing_options) > 0:
        print("The parameters in the configuration file are incomplete!")
        print("Missing options: " + str(missing_options))
        exit()

    raspa_dir = option_dic['raspa_dir']
    cutoffvdm = option_dic['cutoffvdm']
    max_threads = option_dic['max_threads']

    # 如果 raspa_dir 是相对路径，则转换为绝对路径
    if not os.path.isabs(raspa_dir):
        raspa_dir = os.path.join(base_path, raspa_dir)

    if len(raspa_dir) > 0 and not os.path.exists(os.path.join(raspa_dir, "bin", "simulate")):
        print('Invalid RASPA_dir!')
        exit()

    if not os.path.isfile(cif_file_path):
        print('Invalid CIF file path!')
        exit()

    try:
        cutoffvdm = float(cutoffvdm)
    except ValueError:
        print("CutOffVDM must be numerical!")
        exit()

    try:
        max_threads = int(max_threads)
    except ValueError:
        print("max_threads must be integer!")
        exit()

    # 返回修改后的参数列表
    return raspa_dir, cif_file_path, cutoffvdm, max_threads

  