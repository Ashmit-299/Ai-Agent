#!/usr/bin/env python3
"""
GDPR Compliance and Data Deletion Implementation
"""
import os
import json
import time
import logging
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel

# Import authentication using the same pattern as working endpoints
try:
    from .auth import get_current_user_required
except ImportError:
    from app.auth import get_current_user_required

try:
    from .request_middleware import audit_logger
except ImportError:
    class MockAuditLogger:
        def log_action(self, **kwargs):
            pass
    audit_logger = MockAuditLogger()

try:
    from core.s3_storage_adapter import storage_adapter
except ImportError:
    # Fallback storage adapter
    class MockStorageAdapter:
        def list_files(self, segment, max_keys=100):
            return []
        def delete_file(self, segment, filename):
            return True
    storage_adapter = MockStorageAdapter()

try:
    from core.database import DatabaseManager
except ImportError:
    # Fallback database manager
    class MockDatabaseManager:
        def get_user_by_id(self, user_id):
            return None
    DatabaseManager = MockDatabaseManager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/gdpr", tags=["GDPR Compliance"])

class DataDeletionRequest(BaseModel):
    confirm_deletion: bool
    reason: Optional[str] = None

class DataExportResponse(BaseModel):
    user_data: Dict[str, Any]
    export_timestamp: float
    data_types: List[str]

class DataDeletionResponse(BaseModel):
    deleted_data_types: List[str]
    deletion_timestamp: float
    confirmation_id: str
    status: str

class GDPRDataManager:
    """GDPR Data Management Operations"""
    
    def __init__(self):
        try:
            self.db = DatabaseManager()
        except:
            self.db = None
    
    def export_user_data(self, user_id: str) -> Dict[str, Any]:
        """Export all user data for GDPR compliance"""
        
        export_data = {
            "user_id": user_id,
            "export_timestamp": time.time(),
            "data_types": []
        }
        
        # Export user profile
        try:
            user_data = self._export_user_profile(user_id)
            if user_data:
                export_data["user_profile"] = user_data
                export_data["data_types"].append("user_profile")
        except Exception as e:
            logger.error(f"Failed to export user profile for {user_id}: {e}")
        
        # Export content
        try:
            content_data = self._export_user_content(user_id)
            if content_data:
                export_data["content"] = content_data
                export_data["data_types"].append("content")
        except Exception as e:
            logger.error(f"Failed to export content for {user_id}: {e}")
        
        # Export feedback
        try:
            feedback_data = self._export_user_feedback(user_id)
            if feedback_data:
                export_data["feedback"] = feedback_data
                export_data["data_types"].append("feedback")
        except Exception as e:
            logger.error(f"Failed to export feedback for {user_id}: {e}")
        
        # Export scripts
        try:
            scripts_data = self._export_user_scripts(user_id)
            if scripts_data:
                export_data["scripts"] = scripts_data
                export_data["data_types"].append("scripts")
        except Exception as e:
            logger.error(f"Failed to export scripts for {user_id}: {e}")
        
        # Export analytics data
        try:
            analytics_data = self._export_user_analytics(user_id)
            if analytics_data:
                export_data["analytics"] = analytics_data
                export_data["data_types"].append("analytics")
        except Exception as e:
            logger.error(f"Failed to export analytics for {user_id}: {e}")
        
        # Export audit logs
        try:
            audit_data = self._export_user_audit_logs(user_id)
            if audit_data:
                export_data["audit_logs"] = audit_data
                export_data["data_types"].append("audit_logs")
        except Exception as e:
            logger.error(f"Failed to export audit logs for {user_id}: {e}")
        
        return export_data
    
    def delete_user_data(self, user_id: str, request_id: str = None, reason: str = None) -> Dict[str, Any]:
        """Delete all user data for GDPR compliance"""
        
        deletion_results = {
            "user_id": user_id,
            "deletion_timestamp": time.time(),
            "request_id": request_id,
            "reason": reason,
            "deleted_data_types": [],
            "failed_deletions": [],
            "files_deleted": [],
            "status": "in_progress"
        }
        
        # Delete user files from storage
        try:
            deleted_files = self._delete_user_files(user_id)
            deletion_results["files_deleted"] = deleted_files
            deletion_results["deleted_data_types"].append("files")
        except Exception as e:
            logger.error(f"Failed to delete files for {user_id}: {e}")
            deletion_results["failed_deletions"].append(f"files: {str(e)}")
        
        # Delete database records
        database_tables = [
            ("feedback", "user_id"),
            ("scripts", "user_id"),
            ("content", "uploader_id"),
            ("analytics", "user_id"),
            ("audit_logs", "user_id"),
            ("system_logs", "user_id")
        ]
        
        for table, user_column in database_tables:
            try:
                deleted_count = self._delete_user_records(table, user_column, user_id)
                if deleted_count > 0:
                    deletion_results["deleted_data_types"].append(table)
                    logger.info(f"Deleted {deleted_count} records from {table} for user {user_id}")
            except Exception as e:
                logger.error(f"Failed to delete from {table} for {user_id}: {e}")
                deletion_results["failed_deletions"].append(f"{table}: {str(e)}")
        
        # Delete user profile last (to maintain referential integrity)
        try:
            deleted_user = self._delete_user_profile(user_id)
            if deleted_user:
                deletion_results["deleted_data_types"].append("user_profile")
        except Exception as e:
            logger.error(f"Failed to delete user profile for {user_id}: {e}")
            deletion_results["failed_deletions"].append(f"user_profile: {str(e)}")
        
        # Update status
        if len(deletion_results["failed_deletions"]) == 0:
            deletion_results["status"] = "completed"
        elif len(deletion_results["deleted_data_types"]) > 0:
            deletion_results["status"] = "partially_completed"
        else:
            deletion_results["status"] = "failed"
        
        return deletion_results
    
    def _export_user_profile(self, user_id: str) -> Optional[Dict]:
        """Export user profile data"""
        try:
            if self.db:
                user = self.db.get_user_by_id(user_id)
                if user:
                    return {
                        "user_id": user.user_id,
                        "username": user.username,
                        "email": getattr(user, "email", None),
                        "email_verified": getattr(user, "email_verified", False),
                        "created_at": getattr(user, "created_at", None),
                        "last_login": getattr(user, "last_login", None),
                        "role": getattr(user, "role", "user")
                    }
        except Exception as e:
            logger.error(f"Error exporting user profile: {e}")
        return None
    
    def _export_user_content(self, user_id: str) -> List[Dict]:
        """Export user's content"""
        content_list = []
        try:
            # Query content table
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT content_id, title, description, file_path, content_type, 
                           uploaded_at, authenticity_score, current_tags, views, likes, shares
                    FROM content WHERE uploader_id = %s
                """, (user_id,))
                
                for row in cur.fetchall():
                    content_list.append({
                        "content_id": row[0],
                        "title": row[1],
                        "description": row[2],
                        "file_path": row[3],
                        "content_type": row[4],
                        "uploaded_at": row[5],
                        "authenticity_score": row[6],
                        "current_tags": row[7],
                        "views": row[8],
                        "likes": row[9],
                        "shares": row[10]
                    })
                
                cur.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error exporting content: {e}")
        
        return content_list
    
    def _export_user_feedback(self, user_id: str) -> List[Dict]:
        """Export user's feedback"""
        feedback_list = []
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT content_id, event_type, rating, comment, timestamp, reward
                    FROM feedback WHERE user_id = %s
                """, (user_id,))
                
                for row in cur.fetchall():
                    feedback_list.append({
                        "content_id": row[0],
                        "event_type": row[1],
                        "rating": row[2],
                        "comment": row[3],
                        "timestamp": row[4],
                        "reward": row[5]
                    })
                
                cur.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error exporting feedback: {e}")
        
        return feedback_list
    
    def _export_user_scripts(self, user_id: str) -> List[Dict]:
        """Export user's scripts"""
        scripts_list = []
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT script_id, content_id, title, script_type, file_path, 
                           created_at, used_for_generation
                    FROM script WHERE user_id = %s
                """, (user_id,))
                
                for row in cur.fetchall():
                    scripts_list.append({
                        "script_id": row[0],
                        "content_id": row[1],
                        "title": row[2],
                        "script_type": row[3],
                        "file_path": row[4],
                        "created_at": row[5],
                        "used_for_generation": row[6]
                    })
                
                cur.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error exporting scripts: {e}")
        
        return scripts_list
    
    def _export_user_analytics(self, user_id: str) -> List[Dict]:
        """Export user's analytics data"""
        analytics_list = []
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT event_type, content_id, metadata, timestamp, ip_address
                    FROM analytics WHERE user_id = %s
                """, (user_id,))
                
                for row in cur.fetchall():
                    analytics_list.append({
                        "event_type": row[0],
                        "content_id": row[1],
                        "metadata": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4]
                    })
                
                cur.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error exporting analytics: {e}")
        
        return analytics_list
    
    def _export_user_audit_logs(self, user_id: str) -> List[Dict]:
        """Export user's audit logs"""
        audit_list = []
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute("""
                    SELECT action, resource_type, resource_id, timestamp, ip_address, 
                           user_agent, request_id, details, status
                    FROM audit_logs WHERE user_id = %s
                """, (user_id,))
                
                for row in cur.fetchall():
                    audit_list.append({
                        "action": row[0],
                        "resource_type": row[1],
                        "resource_id": row[2],
                        "timestamp": row[3],
                        "ip_address": row[4],
                        "user_agent": row[5],
                        "request_id": row[6],
                        "details": row[7],
                        "status": row[8]
                    })
                
                cur.close()
                conn.close()
        except Exception as e:
            logger.error(f"Error exporting audit logs: {e}")
        
        return audit_list
    
    def _delete_user_files(self, user_id: str) -> List[str]:
        """Delete user files from storage"""
        deleted_files = []
        
        segments = ['uploads', 'scripts', 'storyboards', 'ratings']
        
        for segment in segments:
            try:
                files = storage_adapter.list_files(segment, max_keys=1000)
                
                for file_info in files:
                    filename = file_info['filename']
                    
                    # Check if file belongs to user
                    if user_id in filename:
                        success = storage_adapter.delete_file(segment, filename)
                        if success:
                            deleted_files.append(f"{segment}/{filename}")
                            logger.info(f"Deleted file: {segment}/{filename}")
                
            except Exception as e:
                logger.error(f"Error deleting files from {segment}: {e}")
        
        return deleted_files
    
    def _delete_user_records(self, table: str, user_column: str, user_id: str) -> int:
        """Delete user records from database table"""
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                # Validate table and column names to prevent SQL injection
                allowed_tables = {'content', 'feedback', 'scripts', 'analytics', 'audit_logs', 'system_logs'}
                allowed_columns = {'user_id', 'uploader_id'}
                
                if table not in allowed_tables or user_column not in allowed_columns:
                    raise ValueError(f"Invalid table or column: {table}.{user_column}")
                
                # Use string formatting only for validated table/column names
                query = f"DELETE FROM {table} WHERE {user_column} = %s"
                cur.execute(query, (user_id,))
                deleted_count = cur.rowcount
                
                conn.commit()
                cur.close()
                conn.close()
                
                return deleted_count
                
        except Exception as e:
            logger.error(f"Error deleting from {table}: {e}")
            raise
        
        return 0
    
    def _delete_user_profile(self, user_id: str) -> bool:
        """Delete user profile"""
        try:
            if 'postgresql' in os.getenv("DATABASE_URL", ""):
                import psycopg2
                conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                cur = conn.cursor()
                
                cur.execute('DELETE FROM "user" WHERE user_id = %s', (user_id,))
                deleted_count = cur.rowcount
                
                conn.commit()
                cur.close()
                conn.close()
                
                return deleted_count > 0
                
        except Exception as e:
            logger.error(f"Error deleting user profile: {e}")
            raise
        
        return False

# Global GDPR manager
gdpr_manager = GDPRDataManager()

@router.get("/export-data", response_model=DataExportResponse)
async def export_user_data(
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Export all user data for GDPR compliance"""
    
    user_id = current_user.user_id
    
    try:
        export_data = gdpr_manager.export_user_data(user_id)
        
        # Log the data export
        audit_logger.log_action(
            user_id=user_id,
            action="data_export",
            resource_type="user_data",
            resource_id=user_id,
            request_id=getattr(request.state, 'request_id', None),
            ip_address=request.client.host if request.client else None,
            details={
                "data_types": export_data.get("data_types", []),
                "export_timestamp": export_data.get("export_timestamp")
            }
        )
        
        return DataExportResponse(
            user_data=export_data,
            export_timestamp=export_data.get("export_timestamp", time.time()),
            data_types=export_data.get("data_types", [])
        )
        
    except Exception as e:
        logger.error(f"Data export failed for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Data export failed: {str(e)}"
        )

@router.delete("/delete-data", response_model=DataDeletionResponse)
async def delete_user_data(
    deletion_request: DataDeletionRequest,
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Delete all user data for GDPR compliance"""
    
    user_id = current_user.user_id
    
    if not deletion_request.confirm_deletion:
        raise HTTPException(
            status_code=400,
            detail="Data deletion must be explicitly confirmed"
        )
    
    try:
        request_id = getattr(request.state, 'request_id', None)
        
        deletion_results = gdpr_manager.delete_user_data(
            user_id=user_id,
            request_id=request_id,
            reason=deletion_request.reason
        )
        
        # Log the deletion attempt
        audit_logger.log_action(
            user_id=user_id,
            action="data_deletion",
            resource_type="user_data",
            resource_id=user_id,
            request_id=request_id,
            ip_address=request.client.host if request.client else None,
            details={
                "deleted_data_types": deletion_results["deleted_data_types"],
                "failed_deletions": deletion_results["failed_deletions"],
                "status": deletion_results["status"],
                "reason": deletion_request.reason
            },
            status=deletion_results["status"]
        )
        
        return DataDeletionResponse(
            deleted_data_types=deletion_results["deleted_data_types"],
            deletion_timestamp=deletion_results["deletion_timestamp"],
            confirmation_id=request_id or str(time.time()),
            status=deletion_results["status"]
        )
        
    except Exception as e:
        logger.error(f"Data deletion failed for user {user_id}: {e}")
        
        # Log the failure
        audit_logger.log_action(
            user_id=user_id,
            action="data_deletion",
            resource_type="user_data",
            resource_id=user_id,
            request_id=getattr(request.state, 'request_id', None),
            details={"error": str(e)},
            status="failed"
        )
        
        raise HTTPException(
            status_code=500,
            detail=f"Data deletion failed: {str(e)}"
        )

@router.get("/data-summary")
async def get_user_data_summary(
    request: Request,
    current_user = Depends(get_current_user_required)
):
    """Get summary of user's stored data"""
    
    user_id = current_user.user_id
    
    summary = {
        "user_id": user_id,
        "data_summary": {},
        "total_data_points": 0
    }
    
    try:
        # Count user records in each table
        tables_to_check = [
            ("content", "uploader_id"),
            ("feedback", "user_id"),
            ("scripts", "user_id"),
            ("analytics", "user_id"),
            ("audit_logs", "user_id")
        ]
        
        for table, user_column in tables_to_check:
            try:
                if 'postgresql' in os.getenv("DATABASE_URL", ""):
                    import psycopg2
                    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
                    cur = conn.cursor()
                    
                    # Validate table and column names to prevent SQL injection
                    allowed_tables = {'content', 'feedback', 'scripts', 'analytics', 'audit_logs'}
                    allowed_columns = {'user_id', 'uploader_id'}
                    
                    if table not in allowed_tables or user_column not in allowed_columns:
                        raise ValueError(f"Invalid table or column: {table}.{user_column}")
                    
                    # Use string formatting only for validated table/column names
                    query = f"SELECT COUNT(*) FROM {table} WHERE {user_column} = %s"
                    cur.execute(query, (user_id,))
                    count = cur.fetchone()[0]
                    
                    summary["data_summary"][table] = count
                    summary["total_data_points"] += count
                    
                    cur.close()
                    conn.close()
                    
            except Exception as e:
                logger.error(f"Error counting {table}: {e}")
                summary["data_summary"][table] = "unknown"
        
        # Count files
        file_counts = {}
        segments = ['uploads', 'scripts', 'storyboards']
        
        for segment in segments:
            try:
                files = storage_adapter.list_files(segment, max_keys=1000)
                user_files = [f for f in files if user_id in f['filename']]
                file_counts[segment] = len(user_files)
            except Exception as e:
                logger.error(f"Error counting files in {segment}: {e}")
                file_counts[segment] = "unknown"
        
        summary["data_summary"]["files"] = file_counts
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating data summary for {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Could not generate data summary: {str(e)}"
        )

@router.get("/privacy-policy")
async def get_privacy_policy():
    """Get privacy policy information"""
    
    privacy_info = {
        "policy_version": "1.0",
        "last_updated": "2025-10-03",
        "data_retention_days": 365,
        "data_types_collected": [
            "User profile information (username, email)",
            "Content uploads (scripts, videos, images)", 
            "User interactions (ratings, feedback, analytics)",
            "System logs and audit trails",
            "IP addresses and session data"
        ],
        "data_processing_purposes": [
            "Provide video generation services",
            "Improve AI recommendations",
            "System security and fraud prevention",
            "Analytics and service optimization",
            "Legal compliance and audit trails"
        ],
        "user_rights": [
            "Right to access personal data",
            "Right to rectification of incorrect data",
            "Right to erasure (right to be forgotten)",
            "Right to data portability",
            "Right to object to processing",
            "Right to withdraw consent"
        ],
        "contact_info": {
            "data_protection_officer": "privacy@ai-agent.com",
            "support_email": "support@ai-agent.com"
        },
        "gdpr_endpoints": {
            "export_data": "/gdpr/export-data",
            "delete_data": "/gdpr/delete-data", 
            "data_summary": "/gdpr/data-summary"
        }
    }
    
    return privacy_info