#!/usr/bin/env python3
"""
图表生成器 - 生成可视化图表
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChartGenerator:
    """图表生成器"""
    
    def __init__(self, output_dir: Optional[Path] = None):
        if output_dir is None:
            output_dir = Path(__file__).parent.parent / "charts"
        
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_price_chart(self, prices: List[float], dates: Optional[List[str]] = None,
                            title: str = "价格走势", save: bool = True) -> Optional[str]:
        """
        生成价格走势图
        
        Args:
            prices: 价格列表
            dates: 日期列表（可选）
            title: 图表标题
            save: 是否保存
            
        Returns:
            Optional[str]: 保存的文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')  # 非交互式后端
            
            fig, ax = plt.subplots(figsize=(12, 6))
            
            x = range(len(prices))
            ax.plot(x, prices, linewidth=2, marker='o', markersize=3)
            
            # 设置标题和标签
            ax.set_title(title, fontsize=14, fontweight='bold')
            ax.set_xlabel('时间', fontsize=12)
            ax.set_ylabel('价格', fontsize=12)
            
            # 网格
            ax.grid(True, alpha=0.3)
            
            # 旋转 x 轴标签
            if dates:
                ax.set_xticks(x[::max(1, len(dates)//10)])
                ax.set_xticklabels([dates[i] for i in x[::max(1, len(dates)//10)]], rotation=45)
            
            plt.tight_layout()
            
            if save:
                filename = f"price_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=150, bbox_inches='tight')
                logger.info(f"[图表生成] 价格走势图已保存：{filepath}")
                return str(filepath)
            
            plt.close()
            return None
            
        except ImportError:
            logger.warning("[图表生成] matplotlib 未安装，跳过图表生成")
            return None
        except Exception as e:
            logger.error(f"[图表生成] 生成失败：{e}")
            return None
    
    def generate_prediction_chart(self, current_price: float, 
                                  prediction: Dict[str, Any],
                                  save: bool = True) -> Optional[str]:
        """
        生成预测图表
        
        Args:
            current_price: 当前价格
            prediction: 预测结果
            save: 是否保存
            
        Returns:
            Optional[str]: 保存的文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.use('Agg')
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 当前价格
            ax.bar(['当前价格'], [current_price], color='blue', alpha=0.6, label='当前')
            
            # 预测价格
            pred_price = prediction.get('predicted_price', current_price)
            ax.bar(['预测价格'], [pred_price], color='green', alpha=0.6, label='预测')
            
            # 预测区间
            lower = prediction.get('price_lower', current_price * 0.98)
            upper = prediction.get('price_upper', current_price * 1.02)
            ax.errorbar(['预测价格'], [pred_price], 
                       yerr=[[pred_price - lower], [upper - pred_price]],
                       fmt='none', ecolor='red', capsize=10, linewidth=2, label='预测区间')
            
            # 设置
            ax.set_title(f"价格预测 (置信度：{prediction.get('confidence', 'N/A')})", 
                        fontsize=14, fontweight='bold')
            ax.set_ylabel('价格 (¥)', fontsize=12)
            ax.legend()
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            if save:
                filename = f"prediction_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=150, bbox_inches='tight')
                logger.info(f"[图表生成] 预测图表已保存：{filepath}")
                return str(filepath)
            
            plt.close()
            return None
            
        except Exception as e:
            logger.error(f"[图表生成] 预测图表生成失败：{e}")
            return None
    
    def generate_factor_heatmap(self, scores: Dict[str, float], 
                               weights: Dict[str, float],
                               save: bool = True) -> Optional[str]:
        """
        生成因子热力图
        
        Args:
            scores: 因子得分数值
            weights: 因子权重
            save: 是否保存
            
        Returns:
            Optional[str]: 保存的文件路径
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            import numpy as np
            matplotlib.use('Agg')
            
            factors = list(scores.keys())
            values = [scores[f] for f in factors]
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # 颜色映射（红=看空，绿=看多）
            colors = ['red' if v < 0 else ('green' if v > 0 else 'gray') for v in values]
            intensities = [abs(v) for v in values]
            
            # 柱状图
            bars = ax.bar(factors, values, color=colors, alpha=0.7)
            
            # 添加数值标签
            for i, (bar, v, w) in enumerate(zip(bars, values, [weights.get(f, 0) for f in factors])):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{v:.2f}\n(w={w:.0%})',
                       ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
            
            # 设置
            ax.set_title('因子得分热力图', fontsize=14, fontweight='bold')
            ax.set_ylabel('得分 (-1 到 1)', fontsize=12)
            ax.axhline(y=0, color='black', linewidth=1)
            ax.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            if save:
                filename = f"factor_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                filepath = self.output_dir / filename
                plt.savefig(filepath, dpi=150, bbox_inches='tight')
                logger.info(f"[图表生成] 因子热力图已保存：{filepath}")
                return str(filepath)
            
            plt.close()
            return None
            
        except Exception as e:
            logger.error(f"[图表生成] 因子热力图生成失败：{e}")
            return None
