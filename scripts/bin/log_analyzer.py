#!/usr/bin/env python3
"""
ZackGPT Log Analyzer - Intelligent log querying and analysis
"""
import os
import sys
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class LogAnalyzer:
    """Intelligent log analysis for ZackGPT learning system."""
    
    def __init__(self, db_path: str = "logs/zackgpt_analytics.db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            print(f"❌ Log database not found: {db_path}")
            print("💡 Make sure LOG_AGGREGATION_ENABLED=true and run some interactions first")
            sys.exit(1)
    
    def component_performance_report(self, days: int = 7) -> Dict:
        """Analyze component performance over time."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get component performance data
            query = """
                SELECT component_name, component_type, 
                       AVG(weight_after) as avg_weight,
                       AVG(success_rate_after) as avg_success_rate,
                       COUNT(*) as interactions,
                       AVG(CASE WHEN user_rating >= 4 THEN 1.0 ELSE 0.0 END) as excellent_rate,
                       AVG(CASE WHEN user_rating <= 2 THEN 1.0 ELSE 0.0 END) as poor_rate
                FROM learning_events 
                WHERE event_type IN ('user_rating', 'performance_update')
                  AND timestamp >= datetime('now', '-{} days')
                  AND component_name IS NOT NULL
                GROUP BY component_name, component_type
                ORDER BY avg_weight DESC, interactions DESC
            """.format(days)
            
            results = conn.execute(query).fetchall()
            
            print(f"\n📊 Component Performance Report (Last {days} days)")
            print("=" * 80)
            print(f"{'Component':<30} {'Type':<15} {'Weight':<8} {'Success':<8} {'Uses':<6} {'⭐4-5':<6} {'👎1-2':<6}")
            print("-" * 80)
            
            for row in results:
                print(f"{row['component_name'][:29]:<30} "
                      f"{row['component_type']:<15} "
                      f"{row['avg_weight']:.3f}    "
                      f"{row['avg_success_rate']:.3f}    "
                      f"{row['interactions']:<6} "
                      f"{row['excellent_rate']:.1%}  "
                      f"{row['poor_rate']:.1%}")
            
            return [dict(row) for row in results]
    
    def user_rating_analysis(self, days: int = 7) -> Dict:
        """Analyze user rating patterns."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Rating distribution
            rating_dist = conn.execute("""
                SELECT user_rating, COUNT(*) as count,
                       COUNT(*) * 100.0 / (SELECT COUNT(*) FROM learning_events 
                                          WHERE user_rating IS NOT NULL 
                                            AND timestamp >= datetime('now', '-{} days')) as percentage
                FROM learning_events 
                WHERE user_rating IS NOT NULL 
                  AND timestamp >= datetime('now', '-{} days')
                GROUP BY user_rating 
                ORDER BY user_rating DESC
            """.format(days, days)).fetchall()
            
            # Rating trends over time
            trends = conn.execute("""
                SELECT DATE(timestamp) as date,
                       AVG(user_rating) as avg_rating,
                       COUNT(*) as total_ratings
                FROM learning_events 
                WHERE user_rating IS NOT NULL 
                  AND timestamp >= datetime('now', '-{} days')
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
                LIMIT 10
            """.format(days)).fetchall()
            
            print(f"\n⭐ User Rating Analysis (Last {days} days)")
            print("=" * 50)
            print("Rating Distribution:")
            for row in rating_dist:
                stars = "⭐" * row['user_rating'] if row['user_rating'] > 0 else "⏭️"
                print(f"  {stars} {row['user_rating']}/5: {row['count']:>3} ratings ({row['percentage']:.1f}%)")
            
            print("\nDaily Trends:")
            for row in trends:
                print(f"  {row['date']}: {row['avg_rating']:.2f}/5 avg ({row['total_ratings']} ratings)")
            
            return {
                'distribution': [dict(row) for row in rating_dist],
                'trends': [dict(row) for row in trends]
            }
    
    def learning_efficiency_report(self, days: int = 7) -> Dict:
        """Analyze how efficiently the system is learning."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Learning velocity (weight changes over time)
            velocity = conn.execute("""
                SELECT component_name,
                       MAX(weight_after) - MIN(weight_before) as weight_delta,
                       COUNT(*) as updates,
                       (MAX(weight_after) - MIN(weight_before)) / COUNT(*) as learning_rate
                FROM learning_events 
                WHERE event_type = 'performance_update'
                  AND timestamp >= datetime('now', '-{} days')
                  AND weight_before IS NOT NULL AND weight_after IS NOT NULL
                GROUP BY component_name
                HAVING COUNT(*) > 3
                ORDER BY ABS(weight_delta) DESC
            """.format(days)).fetchall()
            
            print(f"\n🚀 Learning Efficiency Report (Last {days} days)")
            print("=" * 70)
            print(f"{'Component':<30} {'Weight Δ':<10} {'Updates':<8} {'Learn Rate':<12}")
            print("-" * 70)
            
            for row in velocity:
                direction = "📈" if row['weight_delta'] > 0 else "📉" if row['weight_delta'] < 0 else "➡️"
                print(f"{row['component_name'][:29]:<30} "
                      f"{direction} {row['weight_delta']:>6.3f}  "
                      f"{row['updates']:<8} "
                      f"{row['learning_rate']:>8.4f}")
            
            return [dict(row) for row in velocity]
    
    def query_logs(self, event_type: str = None, component: str = None, days: int = 1) -> List[Dict]:
        """General log querying."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            conditions = [f"timestamp >= datetime('now', '-{days} days')"]
            params = []
            
            if event_type:
                conditions.append("event_type = ?")
                params.append(event_type)
            
            if component:
                conditions.append("component_name LIKE ?")
                params.append(f"%{component}%")
            
            query = f"""
                SELECT * FROM learning_events 
                WHERE {' AND '.join(conditions)}
                ORDER BY timestamp DESC
                LIMIT 50
            """
            
            results = conn.execute(query, params).fetchall()
            return [dict(row) for row in results]
    
    def system_health(self) -> Dict:
        """Overall system health metrics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Basic stats
            stats = conn.execute("""
                SELECT 
                    COUNT(*) as total_events,
                    COUNT(DISTINCT component_name) as unique_components,
                    AVG(CASE WHEN user_rating IS NOT NULL THEN user_rating END) as avg_user_rating,
                    COUNT(CASE WHEN user_rating IS NOT NULL THEN 1 END) as total_ratings,
                    COUNT(CASE WHEN event_type = 'component_selected' THEN 1 END) as total_selections
                FROM learning_events 
                WHERE timestamp >= datetime('now', '-7 days')
            """).fetchone()
            
            # Error rate
            errors = conn.execute("""
                SELECT COUNT(*) as error_count
                FROM system_events 
                WHERE level = 'ERROR' 
                  AND timestamp >= datetime('now', '-7 days')
            """).fetchone()
            
            print("\n🏥 System Health Dashboard")
            print("=" * 40)
            print(f"📊 Total Learning Events: {stats['total_events']:,}")
            print(f"🧩 Active Components: {stats['unique_components']}")
            print(f"⭐ Average User Rating: {stats['avg_user_rating']:.2f}/5" if stats['avg_user_rating'] else "⭐ No ratings yet")
            print(f"🎯 Total User Ratings: {stats['total_ratings']:,}")
            print(f"🎲 Component Selections: {stats['total_selections']:,}")
            print(f"❌ Errors (7 days): {errors['error_count']}")
            
            health_score = 100
            if stats['avg_user_rating'] and stats['avg_user_rating'] < 3.0:
                health_score -= 30
            if errors['error_count'] > 10:
                health_score -= 20
            if stats['total_ratings'] < 10:
                health_score -= 10
            
            status = "🟢 Excellent" if health_score >= 90 else "🟡 Good" if health_score >= 70 else "🔴 Needs Attention"
            print(f"💪 Health Score: {health_score}/100 ({status})")
            
            return dict(stats)

def main():
    parser = argparse.ArgumentParser(description="ZackGPT Log Analyzer")
    parser.add_argument("--command", "-c", choices=["performance", "ratings", "efficiency", "health", "query"], 
                       default="health", help="Analysis command to run")
    parser.add_argument("--days", "-d", type=int, default=7, help="Number of days to analyze")
    parser.add_argument("--component", help="Filter by component name")
    parser.add_argument("--event-type", help="Filter by event type")
    
    args = parser.parse_args()
    
    analyzer = LogAnalyzer()
    
    if args.command == "performance":
        analyzer.component_performance_report(args.days)
    elif args.command == "ratings":
        analyzer.user_rating_analysis(args.days)
    elif args.command == "efficiency":
        analyzer.learning_efficiency_report(args.days)
    elif args.command == "health":
        analyzer.system_health()
    elif args.command == "query":
        results = analyzer.query_logs(args.event_type, args.component, args.days)
        print(f"\n🔍 Query Results ({len(results)} events)")
        print("=" * 50)
        for event in results[:10]:  # Show first 10
            print(f"{event['timestamp']} - {event['event_type']} - {event['component_name']}")
            if event['user_rating']:
                print(f"  ⭐ Rating: {event['user_rating']}/5")

if __name__ == "__main__":
    main() 