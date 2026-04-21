"""
Dashboards Package
系统透明化看板模块

包含:
- 数据资产看板 (DataAssetDashboard)
- 预测准确率看板 (AccuracyDashboard)
- 系统进化日志 (EvolutionLog)
- 统一看板服务 (DashboardService)
"""

from .data_asset_dashboard import DataAssetDashboard
from .accuracy_dashboard import AccuracyDashboard
from .evolution_log import EvolutionLog, EvolutionRecord
from .dashboard_service import DashboardService

__all__ = [
    'DataAssetDashboard',
    'AccuracyDashboard',
    'EvolutionLog',
    'EvolutionRecord',
    'DashboardService'
]

__version__ = '1.0.0'
