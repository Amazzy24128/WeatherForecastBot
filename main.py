#!/usr/bin/env python3
"""
天气通知机器人 - 主脚本
每天定时获取南京天气，进行复杂趋势分析，并推送通知
"""
import json
import logging
import os
import sys
import time
import requests
from datetime import datetime, timedelta
from data_manager import DataManager
from weather_analyzer import WeatherAnalyzer
from notifier import ServerChanNotifier


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging. FileHandler('logs/weather_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeatherBot:
    def __init__(self, config_file='config.json'):
        # 确保logs目录存在
        os. makedirs('logs', exist_ok=True)
        
        # 加载配置
        self.config = self.load_config(config_file)
        
        # 初始化各模块
        self.data_manager = DataManager()
        self.analyzer = WeatherAnalyzer(self.config)
        self.notifier = ServerChanNotifier(self.config['serverchan']['sendkey'])
        
        self.qweather_key = self.config['qweather']['api_key']
        self. location_id = self.config['qweather']['location_id']
    
    def load_config(self, config_file):
        """加载配置文件，优先使用环境变量"""
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # 优先使用环境变量中的敏感信息
        if os.getenv('QWEATHER_API_KEY'):
            config['qweather']['api_key'] = os.getenv('QWEATHER_API_KEY')
            logger.info("使用环境变量 QWEATHER_API_KEY")
        
        if os.getenv('SERVERCHAN_SENDKEY'):
            config['serverchan']['sendkey'] = os.getenv('SERVERCHAN_SENDKEY')
            logger.info("使用环境变量 SERVERCHAN_SENDKEY")
        
        # 验证必要的配置
        if not config['qweather']['api_key'] or config['qweather']['api_key'] == 'YOUR_QWEATHER_API_KEY':
            raise ValueError("缺少和风天气API Key，请设置环境变量 QWEATHER_API_KEY 或在 config.json 中配置")
        
        if not config['serverchan']['sendkey'] or config['serverchan']['sendkey'] == 'YOUR_SERVERCHAN_SENDKEY':
            raise ValueError("缺少Server酱SendKey，请设置环境变量 SERVERCHAN_SENDKEY 或在 config. json 中配置")
        
        return config
    
    def should_run(self) -> tuple:
        """判断是否应该运行"""
        # 检查今天是否已运行
        if self. data_manager.check_already_run_today():
            return False, "今天已经运行过"
        
        # 检查时间窗口
        now = datetime.now()
        start_hour = self.config['settings']['execution_window']['start_hour']
        end_hour = self.config['settings']['execution_window']['end_hour']
        
        if not (start_hour <= now.hour < end_hour):
            return False, f"当前时间{now. hour}:{now.minute}不在执行窗口({start_hour}: 00-{end_hour}: 00)"
        
        return True, "可以执行"
    
    def get_weather_forecast(self, retry_times=3) -> dict:
        """
        获取天气预报（带重试）
        """
        # 根据API key判断使用哪个域名
        # 如果是自定义域名的key，使用自定义域名
        if 'ng2mteh6uj' in self.qweather_key or len(self.qweather_key) > 32:
            url = f"https://ng2mteh6uj.re.qweatherapi.com/v7/weather/3d"
        else:
            url = f"https://devapi.qweather.com/v7/weather/3d"
        
        params = {
            'location':  self.location_id,
            'key': self.qweather_key
        }
        
        for attempt in range(retry_times):
            try:
                logger.info(f"正在获取天气数据（第{attempt + 1}次尝试）...")
                response = requests.get(url, params=params, timeout=10)
                data = response.json()
                
                if data.get('code') == '200':
                    # 返回明天的天气（索引1）
                    tomorrow = data['daily'][1]
                    
                    # 格式化数据
                    weather_data = {
                        'date': tomorrow['fxDate'],
                        'temp_max': int(tomorrow['tempMax']),
                        'temp_min': int(tomorrow['tempMin']),
                        'weather':  tomorrow['textDay'],
                        'humidity':  int(tomorrow['humidity']),
                        'precipitation_probability': float(tomorrow.get('precip', 0)),
                        'wind_scale': tomorrow['windScaleDay'],
                        'wind_dir': tomorrow['windDirDay']
                    }
                    
                    logger.info(f"成功获取天气数据:  {weather_data['date']}")
                    return weather_data
                else:
                    logger. error(f"和风天气API返回错误: {data}")
                    
            except Exception as e:
                logger.error(f"获取天气数据失败（第{attempt + 1}次）: {e}")
            
            if attempt < retry_times - 1:
                time.sleep(self.config['settings']['retry_interval'])
        
        raise Exception("获取天气数据失败，已达最大重试次数")
    
    def run(self):
        """主执行流程"""
        try:
            logger.info("=" * 50)
            logger.info("天气机器人启动")
            logger.info("=" * 50)
            
            # 判断是否应该运行
            should_run, reason = self.should_run()
            if not should_run: 
                logger.info(f"跳过执行: {reason}")
                return
            
            logger.info("开始执行天气分析任务")
            
            # 1. 获取明天的天气
            tomorrow_weather = self.get_weather_forecast()
            
            # 2. 获取历史数据
            analysis_days = self.config['settings']['analysis_days']
            historical_data = self.data_manager. get_historical_data(analysis_days)
            logger.info(f"获取到{len(historical_data)}天历史数据")
            
            # 3. 进行复杂趋势分析
            logger.info("开始天气趋势分析...")
            analysis = self.analyzer.analyze_weather_trend(tomorrow_weather, historical_data)
            
            # 4. 生成报告
            report = self.analyzer. format_report(analysis)
            logger.info("天气报告生成完成")
            
            # 5. 发送通知
            logger.info("正在发送通知...")
            title = f"南京明日天气 {tomorrow_weather['date']}"
            success = self.notifier.send(title, report)
            
            if success:
                logger.info("通知发送成功")
                
                # 6. 保存今日数据
                self.data_manager.save_weather_data(tomorrow_weather)
                
                # 7. 更新运行记录
                self.data_manager.update_run_record()
                
                # 8. 清理旧数据
                retention_days = self.config['settings']['data_retention_days']
                self.data_manager.cleanup_old_data(retention_days)
                
                logger.info("任务执行完成")
            else:
                logger.error("通知发送失败")
                
        except Exception as e: 
            logger.error(f"任务执行出错: {e}", exc_info=True)
            
            # 发送错误通知
            try: 
                self.notifier.send(
                    "天气机器人执行失败",
                    f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n错误信息:\n```\n{str(e)}\n```"
                )
            except:
                pass
            
            sys.exit(1)

if __name__ == '__main__':
    bot = WeatherBot()
    bot.run()
