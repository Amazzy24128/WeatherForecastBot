"""
天气分析模块 - 复杂趋势预测和智能建议
"""
import statistics
from typing import List, Dict, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class WeatherAnalyzer:
    def __init__(self, config: dict):
        self.config = config
        self.analysis_config = config.get('analysis', {})
    
    def analyze_weather_trend(self, tomorrow: Dict, historical: List[Dict]) -> Dict:
        """
        复杂天气趋势分析
        
        分析内容：
        1. 温度趋势（升温/降温/波动）
        2. 温差变化
        3. 降水概率趋势
        4. 体感温度分析
        5. 异常天气预警
        6. 穿衣建议
        7. 健康建议
        """
        if not historical:
            return self._generate_simple_report(tomorrow)
        
        analysis = {
            'tomorrow': tomorrow,
            'temperature_trend': self._analyze_temperature_trend(tomorrow, historical),
            'precipitation_trend': self._analyze_precipitation(tomorrow, historical),
            'comfort_analysis': self._analyze_comfort(tomorrow, historical),
            'weather_warnings': self._check_warnings(tomorrow, historical),
            'suggestions': {}
        }
        
        # 生成建议
        analysis['suggestions'] = self._generate_suggestions(analysis)
        
        return analysis
    
    def _analyze_temperature_trend(self, tomorrow: Dict, historical: List[Dict]) -> Dict:
        """温度趋势分析"""
        # 提取历史温度数据
        hist_max_temps = [h['temp_max'] for h in historical if 'temp_max' in h]
        hist_min_temps = [h['temp_min'] for h in historical if 'temp_min' in h]
        
        if not hist_max_temps: 
            return {}
        
        # 计算统计数据
        avg_max_temp = statistics.mean(hist_max_temps)
        avg_min_temp = statistics.mean(hist_min_temps)
        
        # 计算温度变化
        max_temp_change = tomorrow['temp_max'] - avg_max_temp
        min_temp_change = tomorrow['temp_min'] - avg_min_temp
        
        # 计算温度标准差（波动性）
        temp_std = statistics.stdev(hist_max_temps) if len(hist_max_temps) > 1 else 0
        
        # 判断趋势
        trend = "稳定"
        if abs(max_temp_change) > self.analysis_config. get('temp_change_threshold', 3):
            trend = "显著升温" if max_temp_change > 0 else "显著降温"
        elif abs(max_temp_change) > 1.5:
            trend = "小幅升温" if max_temp_change > 0 else "小幅降温"
        
        # 温差分析
        tomorrow_diff = tomorrow['temp_max'] - tomorrow['temp_min']
        avg_hist_diff = avg_max_temp - avg_min_temp
        
        return {
            'trend': trend,
            'max_temp_change': round(max_temp_change, 1),
            'min_temp_change': round(min_temp_change, 1),
            'avg_max_temp': round(avg_max_temp, 1),
            'avg_min_temp': round(avg_min_temp, 1),
            'tomorrow_diff': round(tomorrow_diff, 1),
            'avg_hist_diff': round(avg_hist_diff, 1),
            'volatility': 'high' if temp_std > 5 else 'normal',
            'temp_std': round(temp_std, 1)
        }
    
    def _analyze_precipitation(self, tomorrow: Dict, historical: List[Dict]) -> Dict:
        """降水趋势分析"""
        rain_prob = tomorrow.get('precipitation_probability', 0)
        
        # 统计近期降雨天数
        recent_rainy_days = sum(1 for h in historical 
                                if '雨' in h.get('weather', '') or h.get('precipitation_probability', 0) > 50)
        
        # 判断降雨趋势
        rain_trend = "少雨"
        if rain_prob > 70:
            rain_trend = "大概率降雨"
        elif rain_prob > 40:
            rain_trend = "可能降雨"
        
        return {
            'probability': rain_prob,
            'trend': rain_trend,
            'recent_rainy_days': recent_rainy_days,
            'weather_desc': tomorrow.get('weather', '未知')
        }
    
    def _analyze_comfort(self, tomorrow: Dict, historical: List[Dict]) -> Dict:
        """体感舒适度分析"""
        temp_max = tomorrow['temp_max']
        temp_min = tomorrow['temp_min']
        humidity = tomorrow.get('humidity', 50)
        
        # 简化的体感温度计算（考虑湿度）
        if temp_max > 25:
            apparent_temp = temp_max + (humidity - 50) * 0.1
        else:
            apparent_temp = temp_max
        
        # 舒适度评级
        if 18 <= apparent_temp <= 26:
            comfort_level = "舒适"
        elif 15 <= apparent_temp < 18 or 26 < apparent_temp <= 30:
            comfort_level = "较舒适"
        elif apparent_temp < 15:
            comfort_level = "偏冷"
        else: 
            comfort_level = "偏热"
        
        return {
            'apparent_temp': round(apparent_temp, 1),
            'comfort_level': comfort_level,
            'humidity': humidity,
            'temp_diff': tomorrow['temp_max'] - tomorrow['temp_min']
        }
    
    def _check_warnings(self, tomorrow: Dict, historical: List[Dict]) -> List[str]:
        """异常天气预警"""
        warnings = []
        
        # 极端温度预警
        if tomorrow['temp_max'] >= self.analysis_config.get('hot_warning_temp', 35):
            warnings.append("⚠️ 高温预警：明天最高温度将达到{}°C，请注意防暑降温". format(tomorrow['temp_max']))
        
        if tomorrow['temp_min'] <= self.analysis_config.get('cold_warning_temp', 5):
            warnings.append("⚠️ 低温预警：明天最低温度{}°C，注意保暖防寒".format(tomorrow['temp_min']))
        
        # 温差预警
        temp_diff = tomorrow['temp_max'] - tomorrow['temp_min']
        if temp_diff > self.analysis_config.get('temp_diff_threshold', 10):
            warnings.append("⚠️ 温差较大：早晚温差达{}°C，注意适时增减衣物".format(round(temp_diff, 1)))
        
        # 降水预警
        if tomorrow.get('precipitation_probability', 0) > 70:
            warnings.append("⚠️ 降雨预警：明天降雨概率{}%，记得带伞".format(tomorrow['precipitation_probability']))
        
        # 剧烈温度变化预警
        if historical: 
            last_day = historical[0]
            temp_change = tomorrow['temp_max'] - last_day. get('temp_max', tomorrow['temp_max'])
            if abs(temp_change) > 8:
                direction = "升高" if temp_change > 0 else "降低"
                warnings.append(f"⚠️ 气温剧变：较今天{direction}{abs(round(temp_change, 1))}°C，请注意身体适应")
        
        return warnings
    
    def _generate_suggestions(self, analysis: Dict) -> Dict:
        """生成智能建议"""
        tomorrow = analysis['tomorrow']
        temp_trend = analysis. get('temperature_trend', {})
        comfort = analysis.get('comfort_analysis', {})
        
        # 穿衣建议
        clothing = self._get_clothing_suggestion(
            tomorrow['temp_max'],
            tomorrow['temp_min'],
            comfort.get('apparent_temp', tomorrow['temp_max'])
        )
        
        # 活动建议
        activity = self._get_activity_suggestion(
            tomorrow. get('weather', ''),
            comfort.get('comfort_level', ''),
            tomorrow. get('precipitation_probability', 0)
        )
        
        # 健康建议
        health = self._get_health_suggestion(
            temp_trend.get('trend', ''),
            tomorrow['temp_max'],
            tomorrow['temp_min']
        )
        
        return {
            'clothing': clothing,
            'activity': activity,
            'health': health
        }
    
    def _get_clothing_suggestion(self, temp_max:  float, temp_min: float, apparent_temp: float) -> str:
        """
        穿衣建议（以最低温为主，综合考虑温差）
        """
        temp_diff = temp_max - temp_min
    
        # 【核心】根据最低温判断早晚穿衣（这是出门时的温度）
        if temp_min < -5:
            morning_clothing = "🧥 厚羽绒服 + 毛衣 + 保暖内衣"
        elif temp_min < 0:
            morning_clothing = "🧥 羽绒服/厚棉衣 + 毛衣"
        elif temp_min < 5:
            morning_clothing = "🧥 厚外套/大衣 + 毛衣"
        elif temp_min < 10:
            morning_clothing = "🧥 夹克/风衣 + 卫衣/毛衣"
        elif temp_min < 15:
            morning_clothing = "👔 外套 + 长袖"
        elif temp_min < 20:
            morning_clothing = "👕 长袖衬衫/卫衣"
        elif temp_min < 25:
            morning_clothing = "👕 短袖 + 薄外套（备用）"
        else:
            morning_clothing = "👕 短袖 + 短裤"
    
        # 根据温差给出中午建议
        if temp_diff >= 12:
            # 温差很大，需要洋葱式穿衣
            if temp_max >= 20:
                midday_tip = f"中午可达{temp_max:. 0f}°C，可脱至长袖或短袖"
            elif temp_max >= 15:
                midday_tip = f"中午可达{temp_max:.0f}°C，可脱外套"
            else:
                midday_tip = f"中午可达{temp_max:.0f}°C，可适当减少衣物"
        
            return f"**早晚**：{morning_clothing}\n**温差提示**：⚠️ 温差{temp_diff:.0f}°C，{midday_tip}，建议洋葱式穿衣"
    
        elif temp_diff >= 8:
            # 温差较大
            if temp_max >= 20:
                midday_tip = f"中午{temp_max:.0f}°C较暖，可减少外套"
            else:
                midday_tip = f"中午{temp_max:.0f}°C，可适当减衣"
        
            return f"{morning_clothing}\n💡 温差{temp_diff:.0f}°C，{midday_tip}"
    
        else:
            # 温差不大，全天穿着一致
            return morning_clothing      
   
    def _get_activity_suggestion(self, weather: str, comfort:  str, rain_prob: int) -> str:
        """活动建议"""
        if rain_prob > 70:
            return "☔ 不适宜户外活动，建议室内运动或休息"
        elif '雨' in weather or '雪' in weather:
            return "🏠 户外活动受限，可选择室内健身、看书等"
        elif comfort == "舒适":
            return "🎯 天气宜人，适合户外运动、郊游、散步"
        elif comfort == "较舒适": 
            return "🚶 适合适度户外活动，避免剧烈运动"
        elif comfort == "偏热":
            return "🌡️ 天气较热，户外活动请选择早晚时段，注意防暑"
        elif comfort == "偏冷": 
            return "❄️ 天气较冷，户外活动请做好保暖措施"
        else:
            return "🚶 可适度户外活动"
    
    def _get_health_suggestion(self, trend:  str, temp_max: float, temp_min: float) -> str:
        """健康建议"""
        suggestions = []
        
        if "降温" in trend:
            suggestions.append("气温下降，注意预防感冒")
        elif "升温" in trend:
            suggestions. append("气温上升，注意补充水分")
        
        if temp_max - temp_min > 12:
            suggestions.append("温差较大，心血管疾病患者请注意")
        
        if temp_min < 10:
            suggestions.append("早晨气温低，晨练请做好保暖")
        
        if temp_max > 30:
            suggestions.append("气温较高，避免长时间户外暴晒")
        
        return "💊 " + "；".join(suggestions) if suggestions else "💊 天气适宜，注意规律作息"
    
    def _generate_simple_report(self, tomorrow: Dict) -> Dict:
        """无历史数据时的简单报告"""
        return {
            'tomorrow': tomorrow,
            'temperature_trend': {'trend': '暂无历史数据对比'},
            'suggestions': {
                'clothing': self._get_clothing_suggestion(
                    tomorrow['temp_max'],
                    tomorrow['temp_min'],
                    tomorrow['temp_max']
                ),
                'activity': '暂无建议',
                'health': '注意关注天气变化'
            },
            'weather_warnings': []
        }
    
    def format_report(self, analysis: Dict) -> str:
        """格式化分析报告为Markdown"""
        tomorrow = analysis['tomorrow']
        temp_trend = analysis.get('temperature_trend', {})
        precip = analysis.get('precipitation_trend', {})
        comfort = analysis. get('comfort_analysis', {})
        warnings = analysis.get('weather_warnings', [])
        suggestions = analysis.get('suggestions', {})
        
        report = f"""# 🌤️ 南京明日天气播报

## 📅 基本信息
**日期**:  {tomorrow['date']}  
**天气**: {tomorrow. get('weather', '未知')}  
**温度**: {tomorrow['temp_min']}°C ~ {tomorrow['temp_max']}°C  
**湿度**: {tomorrow.get('humidity', '-')}%  
**风力**: {tomorrow.get('wind_scale', '-')}

"""
        
        # 温度趋势分析
        if temp_trend: 
            report += f"""## 📊 温度趋势分析
**趋势**: {temp_trend.get('trend', '稳定')}  
**较近期平均温度**: 最高温{temp_trend.get('max_temp_change', 0):+.1f}°C，最低温{temp_trend. get('min_temp_change', 0):+.1f}°C  
**早晚温差**: {temp_trend.get('tomorrow_diff', 0):.1f}°C  
**近期平均温差**: {temp_trend.get('avg_hist_diff', 0):.1f}°C  

"""
        
        # 降水分析
        if precip: 
            report += f"""## 🌧️ 降水分析
**降水概率**: {precip. get('probability', 0)}%  
**趋势**: {precip.get('trend', '未知')}  
**近7天降雨**:  {precip.get('recent_rainy_days', 0)}天  

"""
        
        # 体感舒适度
        if comfort: 
            report += f"""## 🌡️ 体感舒适度
**体感温度**: {comfort.get('apparent_temp', 0)}°C  
**舒适等级**: {comfort.get('comfort_level', '未知')}  

"""
        
        # 预警信息
        if warnings: 
            report += "## ⚠️ 天气预警\n"
            for warning in warnings:
                report += f"{warning}\n\n"
        
        # 生活建议
        if suggestions: 
            report += f"""## 💡 生活建议

**穿衣建议**  
{suggestions.get('clothing', '暂无建议')}

**活动建议**  
{suggestions.get('activity', '暂无建议')}

**健康提示**  
{suggestions.get('health', '暂无建议')}

"""
        
        report += f"""---
*数据来源: 和风天气*  
*生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return report
