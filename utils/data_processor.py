"""
数据处理模块
"""

import logging
from typing import List, Tuple, Dict, Any, Optional, Callable
import pandas as pd
from database.db_manager import DatabaseManager
from utils.train_pca import train_pca_model
from utils.random_forest import train_random_forest
from utils.data_importer import DataImporter
from utils.predictor import Predictor
from config import notify

logger = logging.getLogger(__name__)


class DataProcessor:
    """数据处理器"""
    
    def __init__(self):
        self._db: Optional[DatabaseManager] = None
        self._importer: Optional[DataImporter] = None
        self._predictor: Optional[Predictor] = None
        self._init()
    
    def _init(self) -> None:
        """初始化"""
        try:
            self._db = DatabaseManager()
            self._importer = DataImporter(self._db)
            self._predictor = Predictor()
            logger.info("数据处理器初始化完成")
        except Exception as e:
            logger.error(f"初始化失败: {e}")
            notify(f"初始化失败: {e}")
    
    def import_data(
        self,
        excel_file: str,
        table_name: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
        progress_value_callback: Optional[Callable] = None
    ) -> int:
        """
        导入数据

        Args:
            excel_file: Excel 文件路径
            table_name: 目标表名（None 则自动检测）
            progress_callback: 进度回调
            progress_value_callback: 进度值回调

        Returns:
            导入记录数
        """
        self._ensure_init()
        assert self._importer is not None

        pre_read_df = None

        if table_name is None:
            try:
                pre_read_df = pd.read_excel(excel_file)
            except Exception as e:
                raise ValueError(f"无法读取Excel文件: {e}\n请检查文件路径和格式是否正确")
            table_name = self._importer.detect_data_type(pre_read_df)
            if table_name is None:
                raise ValueError("无法识别数据类型，请手动指定表名")

        return self._importer.import_to_table(
            excel_file=excel_file,
            table_name=table_name,
            progress_callback=progress_callback,
            progress_value_callback=progress_value_callback,
            pre_read_df=pre_read_df
        )
    
    def get_all_tables(self) -> List[str]:
        """获取所有表名"""
        self._ensure_init()
        assert self._db is not None
        return self._db.get_all_tables()

    def get_table_data(self, table_name: str) -> Tuple[List[tuple], List[str]]:
        """
        获取表数据

        Args:
            table_name: 表名

        Returns:
            (数据行列表, 列名列表)
        """
        self._ensure_init()
        assert self._db is not None
        return self._db.get_table_data(table_name)
    
    def train_pca(
        self,
        progress_callback: Optional[Callable] = None,
        progress_value_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        训练 PCA 模型
        
        Args:
            progress_callback: 进度回调
            progress_value_callback: 进度值回调
            
        Returns:
            训练结果
        """
        return train_pca_model(
            progress_callback=progress_callback,
            progress_value_callback=progress_value_callback
        )
    
    def train_model(
        self,
        progress_callback: Optional[Callable] = None,
        progress_value_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        训练随机森林模型
        
        Args:
            progress_callback: 进度回调
            progress_value_callback: 进度值回调
            
        Returns:
            训练结果
        """
        return train_random_forest(
            progress_callback=progress_callback,
            progress_value_callback=progress_value_callback
        )
    
    def predict(self, input_data: List[float], data_type: str = 'DGA') -> Tuple[Any, Any]:
        """
        预测故障

        Args:
            input_data: 输入数据
            data_type: 数据类型 (DGA/PD_CH1/PD_CH2/PD_CH3/PD_CH4)

        Returns:
            (故障类型, 故障位置)
        """
        self._ensure_predictor()
        assert self._predictor is not None
        return self._predictor.predict(input_data, data_type)

    def predict_multi(
        self,
        input_data_dict: Dict[str, List[float]],
        progress_callback: Optional[Callable] = None,
        progress_value_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        多类型数据融合预测

        Args:
            input_data_dict: 输入数据字典 {data_type: [values]}
            progress_callback: 进度消息回调
            progress_value_callback: 进度值回调

        Returns:
            预测结果字典
        """
        self._ensure_predictor()
        assert self._predictor is not None
        return self._predictor.predict_multi(
            input_data_dict,
            progress_callback=progress_callback,
            progress_value_callback=progress_value_callback
        )
    
    def reload_predictor(self) -> None:
        """重新加载预测器"""
        self._predictor = Predictor()
        logger.info("预测器重新加载完成")
    
    def _ensure_init(self) -> None:
        """确保已初始化"""
        if self._db is None or self._importer is None:
            self._init()
        if self._db is None or self._importer is None:
            raise RuntimeError("数据处理器初始化失败")
    
    def _ensure_predictor(self) -> None:
        """确保预测器已加载"""
        if self._predictor is None:
            self._predictor = Predictor()
