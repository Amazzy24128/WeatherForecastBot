"""
数据管理模块 - 负责JSON数据的读写和历史数据管理
"""
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class DataManager:
    def __init__(self, data_file='weather_data.json', record_file='run_record.json'):
        self.data_file = data_file
        self.record_file = record_file
        self._ensure_files()
    
    def _ensure_files(self):
        """确保数据文件存在"""
        if not os.path.exists(self.data_file):
            self._save_json(self.data_file, {"records": []})
        if not os.path.exists(self.record_file):
            self._save_json(self. record_file, {})
    
    def _load_json(self, filepath:  str) -> dict:
        """加载JSON文件"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载{filepath}失败: {e}")
            return {}
    
    def _save_json(self, filepath: str, data: dict):
        """保存JSON文件"""
        try:
            # 先保存到临时文件，然后重命名（原子操作）
            temp_file = filepath + '.tmp'
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, filepath)
            logger.info(f"成功保存数据到{filepath}")
        except Exception as e:
            logger. error(f"保存{filepath}失败: {e}")
            raise
    
    def check_already_run_today(self) -> bool:
        """检查今天是否已运行"""
        record = self._load_json(self.record_file)
        today = datetime.now().strftime('%Y-%m-%d')
        last_run = record.get('last_run_date')
        return last_run == today
    
    def update_run_record(self):
        """更新运行记录"""
        record = {
            'last_run_date': datetime.now().strftime('%Y-%m-%d'),
            'last_run_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        self._save_json(self. record_file, record)
    
    def get_historical_data(self, days: int = 7) -> List[Dict]:
        """获取最近N天的历史数据"""
        data = self._load_json(self.data_file)
        records = data.get('records', [])
        
        # 按日期排序
        records.sort(key=lambda x: x['date'], reverse=True)
        
        # 返回最近N天的数据
        return records[: days]
    
    def save_weather_data(self, weather_data: Dict):
        """保存天气数据"""
        data = self._load_json(self.data_file)
        records = data.get('records', [])
        
        # 添加新记录
        records.append(weather_data)
        
        # 按日期排序
        records. sort(key=lambda x: x['date'], reverse=True)
        
        # 只保留最近的记录（防止文件过大）
        records = records[: 60]  # 保留最近60天
        
        data['records'] = records
        self._save_json(self.data_file, data)
    
    def cleanup_old_data(self, days: int = 30):
        """清理超过指定天数的旧数据"""
        data = self._load_json(self. data_file)
        records = data.get('records', [])
        
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        # 过滤掉旧数据
        records = [r for r in records if r['date'] >= cutoff_date]
        
        data['records'] = records
        self._save_json(self.data_file, data)
        logger.info(f"清理了超过{days}天的旧数据，当前保留{len(records)}条记录")
