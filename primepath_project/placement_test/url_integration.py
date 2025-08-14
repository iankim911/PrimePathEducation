"""
URL Integration Module for Placement Test
Provides comprehensive URL pattern integration with extensive logging
Ensures backward compatibility while maintaining clear structure
"""
import json
import logging
from typing import List, Dict, Any
from django.urls import URLPattern, URLResolver

logger = logging.getLogger('placement_test.url_integration')


class URLIntegrationLogger:
    """Enhanced logging for URL pattern integration"""
    
    @staticmethod
    def log_pattern_info(pattern: URLPattern, source: str) -> Dict[str, Any]:
        """Extract and log pattern information"""
        info = {
            "source": source,
            "pattern": str(pattern.pattern),
            "name": pattern.name if hasattr(pattern, 'name') else None,
            "view": None
        }
        
        # Extract view information
        if hasattr(pattern, 'callback'):
            callback = pattern.callback
            if hasattr(callback, '__module__') and hasattr(callback, '__name__'):
                info["view"] = f"{callback.__module__}.{callback.__name__}"
            elif hasattr(callback, 'view_class'):
                info["view"] = f"{callback.view_class.__module__}.{callback.view_class.__name__}"
        
        return info
    
    @staticmethod
    def log_integration_start():
        """Log the start of URL integration"""
        console_log = {
            "event": "URL_INTEGRATION_START",
            "module": "placement_test",
            "timestamp": str(__import__('datetime').datetime.now()),
            "message": "Beginning comprehensive URL pattern integration"
        }
        print(f"[URL_INTEGRATION] {json.dumps(console_log, indent=2)}")
        logger.info("Starting URL integration for placement_test app")
    
    @staticmethod
    def log_pattern_addition(patterns: List, source: str, count: int):
        """Log when patterns are added"""
        console_log = {
            "event": "PATTERNS_ADDED",
            "source": source,
            "count": count,
            "patterns": []
        }
        
        # Extract pattern details for first 5 patterns (to avoid clutter)
        for i, pattern in enumerate(patterns[:5]):
            if isinstance(pattern, URLPattern):
                pattern_info = URLIntegrationLogger.log_pattern_info(pattern, source)
                console_log["patterns"].append(pattern_info)
        
        if count > 5:
            console_log["patterns"].append({"note": f"... and {count - 5} more patterns"})
        
        print(f"[URL_PATTERNS_ADDED] {json.dumps(console_log, indent=2)}")
        logger.info(f"Added {count} patterns from {source}")
    
    @staticmethod
    def log_conflict_check(pattern: str, existing_patterns: List):
        """Log conflict checking"""
        conflicts = []
        for existing in existing_patterns:
            if isinstance(existing, URLPattern):
                if str(existing.pattern) == pattern:
                    conflicts.append({
                        "pattern": str(existing.pattern),
                        "name": existing.name if hasattr(existing, 'name') else None
                    })
        
        if conflicts:
            console_log = {
                "event": "CONFLICT_DETECTED",
                "pattern": pattern,
                "conflicts": conflicts,
                "severity": "warning"
            }
            print(f"[URL_CONFLICT] {json.dumps(console_log, indent=2)}")
            logger.warning(f"Pattern conflict detected for: {pattern}")
        
        return len(conflicts) == 0
    
    @staticmethod
    def log_integration_complete(total_patterns: int, sources: Dict[str, int]):
        """Log completion of URL integration"""
        console_log = {
            "event": "URL_INTEGRATION_COMPLETE",
            "total_patterns": total_patterns,
            "sources": sources,
            "status": "success",
            "message": "All URL patterns successfully integrated"
        }
        print(f"[URL_INTEGRATION_COMPLETE] {json.dumps(console_log, indent=2)}")
        logger.info(f"URL integration complete: {total_patterns} total patterns")
    
    @staticmethod
    def log_error(error: Exception, context: str):
        """Log integration errors"""
        console_log = {
            "event": "URL_INTEGRATION_ERROR",
            "error": str(error),
            "error_type": type(error).__name__,
            "context": context,
            "severity": "error"
        }
        print(f"[URL_INTEGRATION_ERROR] {json.dumps(console_log, indent=2)}")
        logger.error(f"URL integration error in {context}: {error}")


def check_pattern_conflicts(new_patterns: List, existing_patterns: List) -> List[Dict]:
    """
    Check for conflicts between new and existing patterns
    Returns list of conflicts found
    """
    conflicts = []
    
    for new_pattern in new_patterns:
        if not isinstance(new_pattern, URLPattern):
            continue
            
        new_str = str(new_pattern.pattern)
        new_name = new_pattern.name if hasattr(new_pattern, 'name') else None
        
        for existing in existing_patterns:
            if not isinstance(existing, URLPattern):
                continue
                
            existing_str = str(existing.pattern)
            existing_name = existing.name if hasattr(existing, 'name') else None
            
            # Check for path conflicts
            if new_str == existing_str and new_name != existing_name:
                conflicts.append({
                    "type": "path_conflict",
                    "new_pattern": new_str,
                    "new_name": new_name,
                    "existing_pattern": existing_str,
                    "existing_name": existing_name
                })
            
            # Check for name conflicts
            if new_name and existing_name and new_name == existing_name and new_str != existing_str:
                conflicts.append({
                    "type": "name_conflict",
                    "new_pattern": new_str,
                    "new_name": new_name,
                    "existing_pattern": existing_str,
                    "existing_name": existing_name
                })
    
    return conflicts


def integrate_url_patterns(base_patterns: List, additional_patterns: Dict[str, List]) -> List:
    """
    Integrate multiple URL pattern sources with conflict detection and logging
    
    Args:
        base_patterns: Initial list of URL patterns
        additional_patterns: Dictionary of pattern sources to add
        
    Returns:
        Integrated list of URL patterns
    """
    logger_obj = URLIntegrationLogger()
    logger_obj.log_integration_start()
    
    integrated_patterns = list(base_patterns)
    source_counts = {"base": len(base_patterns)}
    
    for source_name, patterns in additional_patterns.items():
        try:
            # Check for conflicts before adding
            conflicts = check_pattern_conflicts(patterns, integrated_patterns)
            
            if conflicts:
                console_log = {
                    "event": "CONFLICTS_FOUND",
                    "source": source_name,
                    "conflict_count": len(conflicts),
                    "conflicts": conflicts[:3]  # Show first 3 conflicts
                }
                if len(conflicts) > 3:
                    console_log["conflicts"].append({"note": f"... and {len(conflicts) - 3} more conflicts"})
                
                print(f"[URL_CONFLICTS] {json.dumps(console_log, indent=2)}")
                logger.warning(f"Found {len(conflicts)} conflicts when adding {source_name}")
                
                # Filter out conflicting patterns
                filtered_patterns = []
                for pattern in patterns:
                    if isinstance(pattern, URLPattern):
                        pattern_str = str(pattern.pattern)
                        pattern_name = pattern.name if hasattr(pattern, 'name') else None
                        
                        # Check if this pattern is in conflicts
                        is_conflicting = False
                        for conflict in conflicts:
                            if (conflict.get('new_pattern') == pattern_str and 
                                conflict.get('new_name') == pattern_name):
                                is_conflicting = True
                                break
                        
                        if not is_conflicting:
                            filtered_patterns.append(pattern)
                    else:
                        filtered_patterns.append(pattern)
                
                patterns = filtered_patterns
                
                if len(filtered_patterns) < len(patterns):
                    print(f"[URL_FILTERED] Filtered out {len(patterns) - len(filtered_patterns)} conflicting patterns from {source_name}")
            
            # Add patterns
            integrated_patterns.extend(patterns)
            source_counts[source_name] = len(patterns)
            logger_obj.log_pattern_addition(patterns, source_name, len(patterns))
            
        except Exception as e:
            logger_obj.log_error(e, f"adding patterns from {source_name}")
            # Continue with other sources even if one fails
            continue
    
    logger_obj.log_integration_complete(len(integrated_patterns), source_counts)
    
    return integrated_patterns


# Console message for module load
print(f"""[URL_INTEGRATION_MODULE] {{
    "module": "url_integration",
    "status": "loaded",
    "features": [
        "Conflict detection",
        "Comprehensive logging",
        "Pattern filtering",
        "Error recovery"
    ],
    "message": "URL integration module ready for use"
}}""")