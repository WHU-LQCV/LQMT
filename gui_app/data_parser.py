"""
数据解析模块
支持多种输入格式：粘贴文本、CSV文件、批量处理
"""

import numpy as np
import pandas as pd
import re
import io
from pathlib import Path


class FormatDetector:
    """自动检测数据格式"""
    
    @staticmethod
    def detect_delimiter(text):
        """
        自动检测分隔符
        
        参数:
            text: str - 输入文本
        
        返回:
            str - 分隔符 ('\t', ',', ' ' 等)
        """
        lines = text.strip().split('\n')
        if len(lines) < 2:
            return ','
        
        first_line = lines[0]
        
        # 统计各种分隔符的数量
        tab_count = first_line.count('\t')
        comma_count = first_line.count(',')
        space_count = len(first_line.split()) - 1
        
        # 选择数量最多的分隔符
        if tab_count > comma_count and tab_count > space_count:
            return '\t'
        elif comma_count > space_count:
            return ','
        else:
            return r'\s+'  # 正则表达式匹配多个空格
    
    @staticmethod
    def detect_format(file_path_or_text):
        """
        检测文件或文本的格式
        
        返回:
            dict - 格式信息
        """
        if isinstance(file_path_or_text, (str, Path)) and Path(file_path_or_text).exists():
            # 文件路径
            file_path = Path(file_path_or_text)
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            # 文本内容
            text = file_path_or_text
        
        delimiter = FormatDetector.detect_delimiter(text)
        
        return {
            'delimiter': delimiter,
            'text': text
        }


class SPDValidator:
    """光谱数据验证器"""
    
    @staticmethod
    def validate_wavelength_range(wavelengths):
        """
        验证波长范围
        
        参数:
            wavelengths: array - 波长数组
        
        返回:
            tuple: (is_valid, message)
        """
        min_wl = np.min(wavelengths)
        max_wl = np.max(wavelengths)
        
        # 检查是否覆盖至少380-780nm范围
        if min_wl > 380:
            return False, f"波长范围起始点({min_wl}nm)大于380nm，可能影响计算准确性"
        
        if max_wl < 780:
            return False, f"波长范围终止点({max_wl}nm)小于780nm，可能影响计算准确性"
        
        return True, "波长范围符合要求"
    
    @staticmethod
    def validate_spd_values(spd_values):
        """
        验证SPD数值有效性
        
        参数:
            spd_values: array - SPD数值数组
        
        返回:
            tuple: (is_valid, message, has_negative)
        """
        has_negative = False
        
        # 检查是否有负值
        if np.any(spd_values < 0):
            has_negative = True
        
        # 检查是否全为零
        if np.all(spd_values == 0):
            return False, "SPD数据全为零", has_negative
        
        # 检查是否有NaN或Inf
        if np.any(np.isnan(spd_values)) or np.any(np.isinf(spd_values)):
            return False, "SPD数据包含无效值(NaN或Inf)", has_negative
        
        if has_negative:
            return True, "SPD数据包含负值（将自动替换为0）", has_negative
        
        return True, "SPD数值有效", has_negative
    
    @staticmethod
    def validate_spd_data(wavelengths, spd_matrix):
        """
        验证完整的SPD数据
        
        参数:
            wavelengths: array - 波长数组
            spd_matrix: 2D array - SPD矩阵，每列为一个样本
        
        返回:
            tuple: (is_valid, messages_list, has_negative)
        """
        messages = []
        is_valid = True
        has_any_negative = False
        
        # 验证波长范围
        valid_wl, msg_wl = SPDValidator.validate_wavelength_range(wavelengths)
        messages.append(msg_wl)
        if not valid_wl:
            is_valid = False
        
        # 验证每个样本的SPD数值
        negative_samples = []
        for i in range(spd_matrix.shape[1]):
            valid_spd, msg_spd, has_negative = SPDValidator.validate_spd_values(spd_matrix[:, i])
            if has_negative:
                has_any_negative = True
                negative_samples.append(i + 1)
            if not valid_spd and "负值" not in msg_spd:
                messages.append(f"样本 {i+1}: {msg_spd}")
                is_valid = False
        
        # 如果有负值，添加一条汇总消息
        if has_any_negative:
            if len(negative_samples) <= 5:
                messages.append(f"以下样本包含负值（将自动替换为0）: {negative_samples}")
            else:
                messages.append(f"共{len(negative_samples)}个样本包含负值（将自动替换为0）")
        
        return is_valid, messages, has_any_negative


class SPDParser:
    """光谱数据解析器"""
    
    def __init__(self):
        self.validator = SPDValidator()
        self.format_detector = FormatDetector()
    
    def parse_text(self, text, has_header=None):
        """
        解析粘贴的文本数据
        
        参数:
            text: str - 输入文本
            has_header: bool - 是否包含表头（None表示自动检测）
        
        返回:
            tuple: (spd_array, sample_names, validation_result)
        """
        try:
            # 检测格式
            format_info = self.format_detector.detect_format(text)
            delimiter = format_info['delimiter']
            
            # 自动检测是否有表头
            if has_header is None:
                lines = text.strip().split('\n')
                if len(lines) > 1:
                    first_line = lines[0].split('\t' if '\t' in lines[0] else (',' if ',' in lines[0] else None))
                    # 如果第一行第一个元素不是数字，可能是表头
                    try:
                        float(first_line[0].strip())
                        has_header = False  # 第一行是数字，没有表头
                    except:
                        has_header = True  # 第一行不是数字，有表头
                else:
                    has_header = False
            
            # 使用pandas读取，优先识别Tab分隔符
            if '\t' in text:
                # 明确使用Tab作为分隔符（Excel复制的格式）
                df = pd.read_csv(io.StringIO(text), sep='\t', header=0 if has_header else None)
            elif delimiter == r'\s+':
                df = pd.read_csv(io.StringIO(text), delim_whitespace=True, header=0 if has_header else None)
            else:
                df = pd.read_csv(io.StringIO(text), sep=delimiter, header=0 if has_header else None)
            
            # 提取波长和SPD数据
            # 假设第一列是波长，后续列是各样本的SPD数据
            wavelengths = df.iloc[:, 0].values
            spd_data = df.iloc[:, 1:].values
            
            # 提取样本名称
            if has_header and df.columns[0] != 0:  # 有表头且不是默认的数字列名
                sample_names = df.columns[1:].tolist()
            else:
                # 没有表头或表头是默认数字，生成默认名称
                sample_names = [f"Spectrum_{i+1:03d}" for i in range(spd_data.shape[1])]
            
            # 验证数据
            is_valid, messages, has_negative = self.validator.validate_spd_data(wavelengths, spd_data)
            
            # 如果有负值，替换为0
            if has_negative:
                spd_data = np.clip(spd_data, 0, None)  # 将负值替换为0
            
            # 构造SPD数组（luxpy格式：第一行为波长，后续行为各样本）
            spd_array = np.vstack([wavelengths, spd_data.T])
            
            return spd_array, sample_names, {'valid': is_valid, 'messages': messages, 'has_negative': has_negative}
            
        except Exception as e:
            return None, None, {'valid': False, 'messages': [f"解析错误: {str(e)}"], 'has_negative': False}
    
    def parse_csv_file(self, file_path):
        """
        解析CSV文件
        
        支持三种格式：
        1. 第一行第一列是"wavelength"之类的字符，第一行其他列是每个spd的ID
        2. 第一行第一列为空，第一行其他列是每个spd的ID
        3. 第一行直接就是数据，第一行第一列是波长数值（如380）
        
        参数:
            file_path: str - CSV文件路径
        
        返回:
            tuple: (spd_array, sample_names, validation_result)
        """
        try:
            # 尝试不同的编码（优先使用 utf-8-sig 以处理 BOM）
            encodings = ['utf-8-sig', 'utf-8', 'gbk', 'gb2312', 'gb18030']
            file_content = None
            used_encoding = None
            
            for encoding in encodings:
                try:
                    with open(file_path, 'r', encoding=encoding) as f:
                        file_content = f.read()
                    used_encoding = encoding
                    break
                except (UnicodeDecodeError, UnicodeError):
                    continue
            
            if file_content is None:
                return None, None, {'valid': False, 'messages': ["无法读取文件，编码格式不支持"]}
            
            # 去除可能的 BOM 字符
            file_content = file_content.lstrip('\ufeff')
            
            # 分析第一行来判断是否有标题行
            lines = file_content.strip().split('\n')
            if len(lines) < 2:
                return None, None, {'valid': False, 'messages': ["文件数据不足"]}
            
            first_line = lines[0].strip()
            second_line = lines[1].strip() if len(lines) > 1 else ''
            
            # 检测分隔符
            if '\t' in first_line:
                delimiter = '\t'
            elif ',' in first_line:
                delimiter = ','
            else:
                delimiter = ','
            
            first_row_values = first_line.split(delimiter)
            first_cell = first_row_values[0].strip().strip('"').strip("'") if first_row_values else ''
            
            # 同时检查第二行第一个单元格
            second_row_values = second_line.split(delimiter) if second_line else []
            second_cell = second_row_values[0].strip().strip('"').strip("'") if second_row_values else ''
            
            # 判断是否有标题行
            # 策略：检查第一行和第二行的第一个单元格
            # 如果第一行第一个单元格是数字，且第二行第一个单元格也是数字，则无标题行
            # 如果第一行第一个单元格为空或非数字，则有标题行
            
            def is_numeric(s):
                """检查字符串是否为数字"""
                if not s:
                    return False
                try:
                    float(s)
                    return True
                except ValueError:
                    return False
            
            has_header = False
            if first_cell == '':
                # 情况2: 第一个单元格为空，有标题行
                has_header = True
            elif is_numeric(first_cell) and is_numeric(second_cell):
                # 第一行和第二行的第一个单元格都是数字，情况3: 无标题行
                has_header = False
            elif not is_numeric(first_cell):
                # 第一个单元格不是数字，情况1: 有标题行
                has_header = True
            else:
                # 其他情况：第一行是数字但第二行不是，可能是异常数据
                # 默认认为无标题行
                has_header = False
            
            # 根据是否有标题行读取CSV
            df = pd.read_csv(io.StringIO(file_content), sep=delimiter, header=0 if has_header else None)
            
            # 提取波长和SPD数据
            wavelengths = df.iloc[:, 0].values
            spd_data = df.iloc[:, 1:].values
            
            # 提取或生成样本名称
            if has_header:
                # 有标题行，使用标题作为样本名称
                sample_names = df.columns[1:].tolist()
                # 确保sample_names是字符串列表
                sample_names = [str(name) for name in sample_names]
            else:
                # 无标题行，自动生成样本名称
                sample_names = [f"Spectrum_{i+1:03d}" for i in range(spd_data.shape[1])]
            
            # 验证数据
            is_valid, messages, has_negative = self.validator.validate_spd_data(wavelengths, spd_data)
            
            # 如果有负值，替换为0
            if has_negative:
                spd_data = np.clip(spd_data, 0, None)  # 将负值替换为0
            
            # 构造SPD数组
            spd_array = np.vstack([wavelengths, spd_data.T])
            
            return spd_array, sample_names, {'valid': is_valid, 'messages': messages, 'has_negative': has_negative}
            
        except Exception as e:
            return None, None, {'valid': False, 'messages': [f"文件读取错误: {str(e)}"], 'has_negative': False}
    
    def parse_batch_files(self, folder_path, file_pattern="*.csv"):
        """
        批量解析文件夹中的CSV文件
        
        参数:
            folder_path: str - 文件夹路径
            file_pattern: str - 文件匹配模式
        
        返回:
            list: [(file_name, spd_array, sample_names, validation_result), ...]
        """
        folder = Path(folder_path)
        if not folder.exists() or not folder.is_dir():
            return []
        
        results = []
        csv_files = list(folder.glob(file_pattern))
        
        for csv_file in csv_files:
            spd_array, sample_names, validation = self.parse_csv_file(csv_file)
            results.append((csv_file.name, spd_array, sample_names, validation))
        
        return results
    
    @staticmethod
    def resample_spd(spd_array, target_start=380, target_end=780, target_step=5):
        """
        重采样SPD数据到目标波长范围和步长
        
        参数:
            spd_array: ndarray - 原始SPD数组
            target_start: int - 目标起始波长
            target_end: int - 目标结束波长
            target_step: int - 目标步长
        
        返回:
            ndarray - 重采样后的SPD数组
        """
        import resampy
        
        original_wl = spd_array[0, :]
        target_wl = np.arange(target_start, target_end + target_step, target_step)
        
        # 对每个样本进行重采样
        resampled_data = []
        for i in range(1, spd_array.shape[0]):
            original_spd = spd_array[i, :]
            # 使用线性插值
            resampled_spd = np.interp(target_wl, original_wl, original_spd)
            resampled_data.append(resampled_spd)
        
        # 构造新的SPD数组
        resampled_array = np.vstack([target_wl] + resampled_data)
        
        return resampled_array


if __name__ == "__main__":
    # 测试代码
    parser = SPDParser()
    
    # 测试文本解析
    test_text = """Wavelength,Sample1,Sample2
380,0.5,0.6
385,0.7,0.8
390,0.9,1.0"""
    
    spd, names, validation = parser.parse_text(test_text)
    print("解析结果:", validation)
    print("样本名称:", names)
