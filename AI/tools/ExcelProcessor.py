"""
Excel文件处理工具
支持读取和解析Excel文件（.xlsx, .xls格式）
"""

import pandas as pd
from typing import Dict, List, Optional, Union
import os


class ExcelProcessor:
    """Excel文件处理器"""

    def __init__(self, file_path: str):
        """
        初始化Excel处理器

        Args:
            file_path: Excel文件路径
        """
        self.file_path = file_path
        self.data: Optional[pd.DataFrame] = None
        self.sheets: Dict[str, pd.DataFrame] = {}

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if not file_path.endswith(('.xlsx', '.xls')):
            raise ValueError("仅支持 .xlsx 和 .xls 格式的Excel文件")

    def read_sheet(self, sheet_name: Union[str, int] = 0, **kwargs) -> pd.DataFrame:
        """
        读取指定的工作表

        Args:
            sheet_name: 工作表名称或索引（默认为第一个工作表）
            **kwargs: pandas.read_excel的其他参数

        Returns:
            DataFrame对象
        """
        try:
            self.data = pd.read_excel(self.file_path, sheet_name=sheet_name, **kwargs)
            return self.data
        except Exception as e:
            raise Exception(f"读取工作表失败: {str(e)}")

    def read_all_sheets(self, **kwargs) -> Dict[str, pd.DataFrame]:
        """
        读取所有工作表

        Args:
            **kwargs: pandas.read_excel的其他参数

        Returns:
            字典，键为工作表名称，值为DataFrame对象
        """
        try:
            self.sheets = pd.read_excel(self.file_path, sheet_name=None, **kwargs)
            return self.sheets
        except Exception as e:
            raise Exception(f"读取所有工作表失败: {str(e)}")

    def get_sheet_names(self) -> List[str]:
        """
        获取所有工作表名称

        Returns:
            工作表名称列表
        """
        try:
            excel_file = pd.ExcelFile(self.file_path)
            return excel_file.sheet_names
        except Exception as e:
            raise Exception(f"获取工作表名称失败: {str(e)}")

    def get_data_as_dict(self) -> List[Dict]:
        """
        将当前数据转换为字典列表

        Returns:
            字典列表，每行数据为一个字典
        """
        if self.data is None:
            raise ValueError("请先使用 read_sheet() 读取数据")
        return self.data.to_dict('records')

    def get_column_names(self) -> List[str]:
        """
        获取列名

        Returns:
            列名列表
        """
        if self.data is None:
            raise ValueError("请先使用 read_sheet() 读取数据")
        return self.data.columns.tolist()

    def get_row_count(self) -> int:
        """
        获取行数

        Returns:
            行数
        """
        if self.data is None:
            raise ValueError("请先使用 read_sheet() 读取数据")
        return len(self.data)

    def filter_data(self, column: str, value) -> pd.DataFrame:
        """
        根据列值筛选数据

        Args:
            column: 列名
            value: 要筛选的值

        Returns:
            筛选后的DataFrame
        """
        if self.data is None:
            raise ValueError("请先使用 read_sheet() 读取数据")
        return self.data[self.data[column] == value]

    def get_summary(self) -> Dict:
        """
        获取数据摘要信息

        Returns:
            包含行数、列数、列名等信息的字典
        """
        if self.data is None:
            raise ValueError("请先使用 read_sheet() 读取数据")

        return {
            "行数": len(self.data),
            "列数": len(self.data.columns),
            "列名": self.data.columns.tolist(),
            "数据类型": self.data.dtypes.to_dict()
        }


# 使用示例
if __name__ == "__main__":
    # 示例1: 读取单个工作表
    processor = ExcelProcessor("./example.xlsx")
    data = processor.read_sheet()
    print("数据预览:")
    print(data.head())

    # 示例2: 获取所有工作表名称
    sheet_names = processor.get_sheet_names()
    print(f"\n工作表列表: {sheet_names}")

    # 示例3: 读取所有工作表
    all_sheets = processor.read_all_sheets()
    for sheet_name, sheet_data in all_sheets.items():
        print(f"\n工作表 '{sheet_name}' 有 {len(sheet_data)} 行数据")

    # 示例4: 获取数据摘要
    summary = processor.get_summary()
    print(f"\n数据摘要: {summary}")

    # 示例5: 转换为字典列表
    dict_data = processor.get_data_as_dict()
    print(f"\n前3条记录: {dict_data[:3]}")
