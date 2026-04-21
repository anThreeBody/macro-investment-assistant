#!/usr/bin/env python3
"""
重大事件日历 (Event Calendar)

收集和展示未来 7 天可能影响市场的重大事件

事件类型:
- 经济数据（CPI、GDP、就业等）
- 央行政策（议息会议、降准降息等）
- 政治事件（选举、会议等）
- 公司财报（重要公司财报季）
- 其他（地缘政治、自然灾害等）
"""

import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class MarketEvent:
    """市场事件"""
    date: str  # YYYY-MM-DD
    time: Optional[str]  # HH:MM
    title: str
    country: str  # CN/US/EU/JP 等
    impact: str  # 高/中/低
    affected_assets: List[str]
    actual: Optional[str] = None
    forecast: Optional[str] = None
    previous: Optional[str] = None
    category: str = "经济数据"  # 经济数据/央行政策/政治事件/公司财报/其他


class EventCalendar:
    """事件日历管理器"""
    
    def __init__(self):
        # 事件数据文件路径
        self.data_file = Path(__file__).parent.parent / "data" / "event_calendar.json"
        
        # 重要性映射
        self.impact_emoji = {
            '高': '🔴',
            '中': '🟡',
            '低': '🟢'
        }
        
        # 国家/地区映射
        self.country_names = {
            'CN': '中国',
            'US': '美国',
            'EU': '欧盟',
            'JP': '日本',
            'UK': '英国',
            'Global': '全球'
        }
        
        # 资产类别映射
        self.asset_names = {
            '黄金': '黄金',
            '美元': '美元',
            'A 股': 'A 股',
            '港股': '港股',
            '美股': '美股',
            '人民币': '人民币',
            '原油': '原油',
            '债券': '债券',
            '欧元': '欧元'
        }
        
        logger.info("[事件日历] 初始化完成")
    
    def get_upcoming_events(self, days: int = 7) -> List[MarketEvent]:
        """
        获取未来 N 天的重大事件
        
        Args:
            days: 未来天数，默认 7 天
        
        Returns:
            List[MarketEvent]: 事件列表，按日期和重要性排序
        """
        logger.info(f"[事件日历] 获取未来 {days} 天事件...")
        
        events = []
        
        # 1. 从文件加载已配置的事件
        events.extend(self._load_events_from_file(days))
        
        # 2. 添加定期事件（如每月 CPI、每季 GDP 等）
        events.extend(self._generate_recurring_events(days))
        
        # 3. 按日期和重要性排序
        events.sort(key=lambda e: (e.date, 0 if e.impact == '高' else 1 if e.impact == '中' else 2))
        
        logger.info(f"[事件日历] 找到 {len(events)} 个事件")
        
        return events
    
    def _load_events_from_file(self, days: int) -> List[MarketEvent]:
        """从 JSON 文件加载事件"""
        events = []
        
        if not self.data_file.exists():
            logger.warning(f"[事件日历] 数据文件不存在：{self.data_file}")
            return events
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            today = datetime.now().date()
            end_date = today + timedelta(days=days)
            
            for event_data in data.get('events', []):
                event_date = datetime.strptime(event_data['date'], '%Y-%m-%d').date()
                
                # 只返回未来 N 天的事件
                if today <= event_date <= end_date:
                    event = MarketEvent(
                        date=event_data['date'],
                        time=event_data.get('time'),
                        title=event_data['title'],
                        country=event_data.get('country', 'Global'),
                        impact=event_data.get('impact', '中'),
                        affected_assets=event_data.get('affected_assets', []),
                        actual=event_data.get('actual'),
                        forecast=event_data.get('forecast'),
                        previous=event_data.get('previous'),
                        category=event_data.get('category', '经济数据')
                    )
                    events.append(event)
            
            logger.info(f"[事件日历] 从文件加载 {len(events)} 个事件")
            
        except Exception as e:
            logger.error(f"[事件日历] 加载文件失败：{e}")
        
        return events
    
    def _generate_recurring_events(self, days: int) -> List[MarketEvent]:
        """生成定期事件（基于规则）"""
        events = []
        today = datetime.now().date()
        end_date = today + timedelta(days=days)
        
        # 美国 CPI（每月 10-15 日左右）
        cpi_date = self._find_date_in_range(today, end_date, day_range=(10, 15))
        if cpi_date:
            events.append(MarketEvent(
                date=cpi_date.strftime('%Y-%m-%d'),
                time="20:30",
                title="美国 CPI 数据",
                country="US",
                impact="高",
                affected_assets=["黄金", "美元", "美股"],
                category="经济数据"
            ))
        
        # 中国 GDP（每季度首月 15-20 日左右）
        current_month = today.month
        if current_month in [1, 4, 7, 10]:  # 季度首月
            gdp_date = self._find_date_in_range(today, end_date, day_range=(15, 20))
            if gdp_date:
                events.append(MarketEvent(
                    date=gdp_date.strftime('%Y-%m-%d'),
                    time="10:00",
                    title="中国季度 GDP",
                    country="CN",
                    impact="高",
                    affected_assets=["A 股", "人民币"],
                    category="经济数据"
                ))
        
        # 美联储议息会议（每年 8 次，简化处理：每月 15-20 日可能）
        fed_date = self._find_date_in_range(today, end_date, day_range=(15, 20))
        if fed_date and today.month % 2 == 0:  # 简化：偶数月可能有会议
            events.append(MarketEvent(
                date=fed_date.strftime('%Y-%m-%d'),
                time="02:00",
                title="美联储议息会议",
                country="US",
                impact="高",
                affected_assets=["黄金", "美元", "美股"],
                category="央行政策"
            ))
        
        # 中国 PMI（每月最后一天或次月 1 日）
        pmi_date = self._find_date_in_range(today, end_date, day_range=(1, 2))
        if pmi_date:
            events.append(MarketEvent(
                date=pmi_date.strftime('%Y-%m-%d'),
                time="09:30",
                title="中国 PMI 数据",
                country="CN",
                impact="中",
                affected_assets=["A 股"],
                category="经济数据"
            ))
        
        # 美国非农就业（每月第一个周五）
        first_friday = self._find_first_friday(today, end_date)
        if first_friday:
            events.append(MarketEvent(
                date=first_friday.strftime('%Y-%m-%d'),
                time="20:30",
                title="美国非农就业数据",
                country="US",
                impact="高",
                affected_assets=["美元", "黄金", "美股"],
                category="经济数据"
            ))
        
        return events
    
    def _find_date_in_range(self, start: datetime.date, end: datetime.date, 
                           day_range: tuple) -> Optional[datetime.date]:
        """在日期范围内查找指定日期范围的日期"""
        current = start
        while current <= end:
            if day_range[0] <= current.day <= day_range[1]:
                return current
            current += timedelta(days=1)
        return None
    
    def _find_first_friday(self, start: datetime.date, end: datetime.date) -> Optional[datetime.date]:
        """查找范围内第一个周五"""
        current = start
        while current <= end:
            if current.weekday() == 4:  # 周五
                return current
            current += timedelta(days=1)
        return None
    
    def get_events_by_date(self, events: List[MarketEvent]) -> Dict[str, List[MarketEvent]]:
        """按日期分组事件"""
        by_date = {}
        for event in events:
            if event.date not in by_date:
                by_date[event.date] = []
            by_date[event.date].append(event)
        return by_date
    
    def format_date(self, date_str: str) -> str:
        """格式化日期显示"""
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d')
            today = datetime.now().date()
            
            if date.date() == today:
                return "今天"
            elif date.date() == today + timedelta(days=1):
                return "明天"
            else:
                weekday = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'][date.weekday()]
                return f"{date.month}月{date.day}日 ({weekday})"
        except:
            return date_str
    
    def create_sample_data(self) -> Dict:
        """创建示例事件数据"""
        today = datetime.now().date()
        
        events = []
        
        # 未来 7 天的示例事件
        sample_events = [
            {
                'date': (today + timedelta(days=3)).strftime('%Y-%m-%d'),
                'time': '20:30',
                'title': '美国 CPI 数据',
                'country': 'US',
                'impact': '高',
                'affected_assets': ['黄金', '美元', '美股'],
                'category': '经济数据',
                'forecast': '3.2%',
                'previous': '3.3%'
            },
            {
                'date': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
                'time': '10:00',
                'title': '中国一季度 GDP',
                'country': 'CN',
                'impact': '高',
                'affected_assets': ['A 股', '人民币'],
                'category': '经济数据',
                'forecast': '5.0%',
                'previous': '5.2%'
            },
            {
                'date': (today + timedelta(days=7)).strftime('%Y-%m-%d'),
                'time': '02:00',
                'title': '美联储议息会议',
                'country': 'US',
                'impact': '高',
                'affected_assets': ['黄金', '美元', '美股'],
                'category': '央行政策'
            },
            {
                'date': (today + timedelta(days=2)).strftime('%Y-%m-%d'),
                'time': '09:30',
                'title': '中国 LPR 报价',
                'country': 'CN',
                'impact': '中',
                'affected_assets': ['A 股', '人民币'],
                'category': '央行政策',
                'forecast': '3.45%',
                'previous': '3.45%'
            },
            {
                'date': (today + timedelta(days=4)).strftime('%Y-%m-%d'),
                'time': '16:30',
                'title': '欧元区 PMI 数据',
                'country': 'EU',
                'impact': '中',
                'affected_assets': ['欧元'],
                'category': '经济数据'
            }
        ]
        
        return {'events': sample_events}
    
    def save_sample_data(self):
        """保存示例数据到文件"""
        data = self.create_sample_data()
        
        # 确保 data 目录存在
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"[事件日历] 示例数据已保存到：{self.data_file}")


def main():
    """测试主函数"""
    print("=" * 70)
    print("📅 重大事件日历")
    print("=" * 70)
    print()
    
    calendar = EventCalendar()
    
    # 创建示例数据
    calendar.save_sample_data()
    
    # 获取未来 7 天事件
    events = calendar.get_upcoming_events(days=7)
    
    if not events:
        print("未来 7 天暂无重大事件")
        return
    
    print(f"未来 7 天共 {len(events)} 个重大事件:")
    print()
    
    # 按日期分组
    by_date = calendar.format_events_by_date(events)
    
    for date_str, date_events in sorted(by_date.items()):
        display_date = calendar.format_date(date_str)
        print(f"**{display_date}** ({date_str})")
        print()
        print("| 时间 | 事件 | 影响资产 | 重要性 |")
        print("|------|------|----------|--------|")
        
        for event in date_events:
            time_str = event.time if event.time else "-"
            assets_str = ", ".join(event.affected_assets)
            impact_emoji = calendar.impact_emoji.get(event.impact, '⚪')
            
            print(f"| {time_str} | {event.title} | {assets_str} | {impact_emoji} {event.impact} |")
        
        print()
    
    print("=" * 70)
    
    return events


# 添加缺失的方法
def format_events_by_date(self, events: List[MarketEvent]) -> Dict[str, List[MarketEvent]]:
    """按日期分组事件"""
    by_date = {}
    for event in events:
        if event.date not in by_date:
            by_date[event.date] = []
        by_date[event.date].append(event)
    return by_date


# 绑定方法到类
EventCalendar.format_events_by_date = format_events_by_date


if __name__ == "__main__":
    main()
