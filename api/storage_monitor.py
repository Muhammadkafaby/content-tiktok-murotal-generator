import shutil
import logging
from pathlib import Path
from api.config import DATA_DIR

logger = logging.getLogger(__name__)

# Threshold in bytes (1GB)
LOW_STORAGE_THRESHOLD = 1 * 1024 * 1024 * 1024


def get_storage_info() -> dict:
    """Get storage information"""
    total, used, free = shutil.disk_usage(DATA_DIR)
    
    return {
        "total_bytes": total,
        "used_bytes": used,
        "free_bytes": free,
        "total_gb": round(total / (1024**3), 2),
        "used_gb": round(used / (1024**3), 2),
        "free_gb": round(free / (1024**3), 2),
        "usage_percent": round(used / total * 100, 1)
    }


def check_storage() -> bool:
    """Check if storage is sufficient. Returns True if OK, False if low."""
    info = get_storage_info()
    
    if info["free_bytes"] < LOW_STORAGE_THRESHOLD:
        logger.warning(
            f"Low storage warning! Free: {info['free_gb']}GB, "
            f"Threshold: {LOW_STORAGE_THRESHOLD / (1024**3)}GB"
        )
        return False
    
    return True


def is_low_storage() -> bool:
    """Check if storage is below threshold"""
    info = get_storage_info()
    return info["free_bytes"] < LOW_STORAGE_THRESHOLD


def get_directory_size(path: Path) -> int:
    """Get total size of a directory in bytes"""
    total = 0
    if path.exists():
        for file in path.rglob('*'):
            if file.is_file():
                total += file.stat().st_size
    return total
