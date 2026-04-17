"""
Système de logging avec rotation et niveaux
"""
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

def setup_logger(name='trading_bot', log_file=None, max_bytes=10*1024*1024):
    """
    Configure un logger avec rotation
    
    Args:
        name: Nom du logger
        log_file: Chemin fichier log
        max_bytes: Taille max avant rotation (10MB par défaut)
    """
    os.makedirs('logs', exist_ok=True)
    
    if log_file is None:
        log_file = f'logs/{name}_{datetime.now().strftime("%Y%m%d")}.log'
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Éviter doublons
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler avec rotation
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=max_bytes,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_log_content(log_file='logs/trading_bot.log', lines=200):
    """
    Récupère les dernières lignes du log
    
    Args:
        log_file: Chemin du fichier
        lines: Nombre de lignes à récupérer
    
    Returns:
        Liste des lignes
    """
    try:
        if not os.path.exists(log_file):
            return [f"⚠️ Fichier {log_file} introuvable"]
        
        with open(log_file, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            return all_lines[-lines:] if len(all_lines) > lines else all_lines
    except Exception as e:
        return [f"❌ Erreur lecture logs: {str(e)}"]
