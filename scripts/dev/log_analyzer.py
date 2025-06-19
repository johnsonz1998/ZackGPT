#!/usr/bin/env python3
"""
ZackGPT Log Analyzer - Intelligent log querying and analysis
"""
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any
import argparse
from pymongo import MongoClient

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

class LogAnalyzer:
    """Intelligent log analysis for ZackGPT learning system."""
    
    def __init__(self, mongo_uri: str = None, db_name: str = "zackgpt"):
        self.mongo_uri = mongo_uri or os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            
            # Test connection
            self.client.admin.command('ping')
            
            # Check if collections exist and have data
            collections = ['prompt_evolution', 'system_logs', 'performance_metrics']
            total_docs = sum(self.db[col].count_documents({}) for col in collections)
            
            if total_docs == 0:
                print("❌ No analytics data found in MongoDB")
                print("💡 Make sure LOG_AGGREGATION_ENABLED=true and run some interactions first")
                sys.exit(1)
                
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("💡 Make sure MongoDB is running and accessible")
            sys.exit(1)
    
    def component_performance_report(self, days: int = 7) -> Dict:
        """Analyze component performance over time."""
        # Get datetime cutoff
        cutoff = datetime.now() - timedelta(days=days)
        
        # Aggregation pipeline for component performance
        pipeline = [
            {
                "$match": {
                    "event_type": {"$in": ["user_rating", "performance_update"]},
                    "created_at": {"$gte": cutoff},
                    "component_name": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": {
                        "component_name": "$component_name",
                        "component_type": "$component_type"
                    },
                    "avg_weight": {"$avg": "$weight_after"},
                    "avg_success_rate": {"$avg": "$success_rate_after"},
                    "interactions": {"$sum": 1},
                    "excellent_ratings": {
                        "$sum": {"$cond": [{"$gte": ["$user_rating", 4]}, 1, 0]}
                    },
                    "poor_ratings": {
                        "$sum": {"$cond": [{"$lte": ["$user_rating", 2]}, 1, 0]}
                    },
                    "total_ratings": {
                        "$sum": {"$cond": [{"$ne": ["$user_rating", None]}, 1, 0]}
                    }
                }
            },
            {
                "$project": {
                    "component_name": "$_id.component_name",
                    "component_type": "$_id.component_type",
                    "avg_weight": 1,
                    "avg_success_rate": 1,
                    "interactions": 1,
                    "excellent_rate": {
                        "$cond": [
                            {"$gt": ["$total_ratings", 0]},
                            {"$divide": ["$excellent_ratings", "$total_ratings"]},
                            0
                        ]
                    },
                    "poor_rate": {
                        "$cond": [
                            {"$gt": ["$total_ratings", 0]},
                            {"$divide": ["$poor_ratings", "$total_ratings"]},
                            0
                        ]
                    }
                }
            },
            {"$sort": {"avg_weight": -1, "interactions": -1}}
        ]
        
        results = list(self.db.prompt_evolution.aggregate(pipeline))
        
        print(f"\n📊 Component Performance Report (Last {days} days)")
        print("=" * 80)
        print(f"{'Component':<30} {'Type':<15} {'Weight':<8} {'Success':<8} {'Uses':<6} {'⭐4-5':<6} {'👎1-2':<6}")
        print("-" * 80)
        
        for row in results:
            name = row['component_name'][:29] if row['component_name'] else 'N/A'
            comp_type = row['component_type'] or 'N/A'
            weight = row.get('avg_weight', 0) or 0
            success = row.get('avg_success_rate', 0) or 0
            interactions = row.get('interactions', 0)
            excellent = row.get('excellent_rate', 0)
            poor = row.get('poor_rate', 0)
            
            print(f"{name:<30} "
                  f"{comp_type:<15} "
                  f"{weight:.3f}    "
                  f"{success:.3f}    "
                  f"{interactions:<6} "
                  f"{excellent:.1%}  "
                  f"{poor:.1%}")
        
        return results
    
    def user_rating_analysis(self, days: int = 7) -> Dict:
        """Analyze user rating patterns."""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Rating distribution
        rating_pipeline = [
            {
                "$match": {
                    "user_rating": {"$ne": None},
                    "created_at": {"$gte": cutoff}
                }
            },
            {
                "$group": {
                    "_id": "$user_rating",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}}
        ]
        
        rating_dist = list(self.db.prompt_evolution.aggregate(rating_pipeline))
        total_ratings = sum(r['count'] for r in rating_dist)
        
        # Daily trends
        trends_pipeline = [
            {
                "$match": {
                    "user_rating": {"$ne": None},
                    "created_at": {"$gte": cutoff}
                }
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$created_at"
                        }
                    },
                    "avg_rating": {"$avg": "$user_rating"},
                    "total_ratings": {"$sum": 1}
                }
            },
            {"$sort": {"_id": -1}},
            {"$limit": 10}
        ]
        
        trends = list(self.db.prompt_evolution.aggregate(trends_pipeline))
        
        print(f"\n⭐ User Rating Analysis (Last {days} days)")
        print("=" * 50)
        print("Rating Distribution:")
        for row in rating_dist:
            rating = row['_id']
            count = row['count']
            percentage = (count / total_ratings * 100) if total_ratings > 0 else 0
            stars = "⭐" * rating if rating > 0 else "⏭️"
            print(f"  {stars} {rating}/5: {count:>3} ratings ({percentage:.1f}%)")
        
        print("\nDaily Trends:")
        for row in trends:
            date = row['_id']
            avg_rating = row['avg_rating']
            total = row['total_ratings']
            print(f"  {date}: {avg_rating:.2f}/5 avg ({total} ratings)")
        
        return {
            'distribution': rating_dist,
            'trends': trends
        }
    
    def learning_efficiency_report(self, days: int = 7) -> Dict:
        """Analyze how efficiently the system is learning."""
        cutoff = datetime.now() - timedelta(days=days)
        
        # Learning velocity pipeline
        velocity_pipeline = [
            {
                "$match": {
                    "event_type": "performance_update",
                    "created_at": {"$gte": cutoff},
                    "weight_before": {"$ne": None},
                    "weight_after": {"$ne": None}
                }
            },
            {
                "$group": {
                    "_id": "$component_name",
                    "max_weight": {"$max": "$weight_after"},
                    "min_weight": {"$min": "$weight_before"},
                    "updates": {"$sum": 1}
                }
            },
            {
                "$match": {"updates": {"$gt": 3}}
            },
            {
                "$project": {
                    "component_name": "$_id",
                    "weight_delta": {"$subtract": ["$max_weight", "$min_weight"]},
                    "updates": 1,
                    "learning_rate": {
                        "$divide": [
                            {"$subtract": ["$max_weight", "$min_weight"]},
                            "$updates"
                        ]
                    }
                }
            },
            {
                "$sort": {
                    "weight_delta": -1
                }
            }
        ]
        
        velocity = list(self.db.prompt_evolution.aggregate(velocity_pipeline))
        
        print(f"\n🚀 Learning Efficiency Report (Last {days} days)")
        print("=" * 70)
        print(f"{'Component':<30} {'Weight Δ':<10} {'Updates':<8} {'Learn Rate':<12}")
        print("-" * 70)
        
        for row in velocity:
            name = row['component_name'][:29] if row['component_name'] else 'N/A'
            weight_delta = row.get('weight_delta', 0)
            updates = row.get('updates', 0)
            learning_rate = row.get('learning_rate', 0)
            
            direction = "📈" if weight_delta > 0 else "📉" if weight_delta < 0 else "➡️"
            print(f"{name:<30} "
                  f"{direction} {weight_delta:>6.3f}  "
                  f"{updates:<8} "
                  f"{learning_rate:>8.4f}")
        
        return velocity
    
    def query_logs(self, event_type: str = None, component: str = None, days: int = 1) -> List[Dict]:
        """General log querying."""
        cutoff = datetime.now() - timedelta(days=days)
        
        match_conditions = {"created_at": {"$gte": cutoff}}
        
        if event_type:
            match_conditions["event_type"] = event_type
        
        if component:
            match_conditions["component_name"] = {"$regex": component, "$options": "i"}
        
        results = list(
            self.db.prompt_evolution.find(match_conditions)
            .sort("created_at", -1)
            .limit(50)
        )
        
        # Convert ObjectId to string for JSON serialization
        for result in results:
            result['_id'] = str(result['_id'])
        
        return results
    
    def system_health(self) -> Dict:
        """Overall system health metrics."""
        cutoff = datetime.now() - timedelta(days=7)
        
        # Basic stats
        stats_pipeline = [
            {
                "$match": {"created_at": {"$gte": cutoff}}
            },
            {
                "$group": {
                    "_id": None,
                    "total_events": {"$sum": 1},
                    "avg_user_rating": {"$avg": "$user_rating"},
                    "total_ratings": {
                        "$sum": {"$cond": [{"$ne": ["$user_rating", None]}, 1, 0]}
                    },
                    "total_selections": {
                        "$sum": {"$cond": [{"$eq": ["$event_type", "component_selected"]}, 1, 0]}
                    },
                    "unique_components": {"$addToSet": "$component_name"}
                }
            },
            {
                "$project": {
                    "total_events": 1,
                    "avg_user_rating": 1,
                    "total_ratings": 1,
                    "total_selections": 1,
                    "unique_components": {"$size": "$unique_components"}
                }
            }
        ]
        
        stats_result = list(self.db.prompt_evolution.aggregate(stats_pipeline))
        stats = stats_result[0] if stats_result else {}
        
        # Error count
        error_count = self.db.system_logs.count_documents({
            "level": "ERROR",
            "created_at": {"$gte": cutoff}
        })
        
        print("\n🏥 System Health Dashboard")
        print("=" * 40)
        print(f"📊 Total Learning Events: {stats.get('total_events', 0):,}")
        print(f"🧩 Active Components: {stats.get('unique_components', 0)}")
        
        avg_rating = stats.get('avg_user_rating')
        if avg_rating:
            print(f"⭐ Average User Rating: {avg_rating:.2f}/5")
        else:
            print("⭐ No ratings yet")
            
        print(f"🎯 Total User Ratings: {stats.get('total_ratings', 0):,}")
        print(f"🎲 Component Selections: {stats.get('total_selections', 0):,}")
        print(f"❌ Errors (7 days): {error_count}")
        
        health_score = 100
        if avg_rating and avg_rating < 3.0:
            health_score -= 30
        if error_count > 10:
            health_score -= 20
        
        status = "🟢 Excellent" if health_score >= 80 else "🟡 Good" if health_score >= 60 else "🔴 Needs Attention"
        print(f"\n🏥 Health Score: {health_score}/100 {status}")
        
        return stats

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
            timestamp = event.get('timestamp', event.get('created_at', 'N/A'))
            event_type = event.get('event_type', 'N/A')
            component = event.get('component_name', 'N/A')
            print(f"{timestamp} - {event_type} - {component}")
            if event.get('user_rating'):
                print(f"  ⭐ Rating: {event['user_rating']}/5")

if __name__ == "__main__":
    main() 