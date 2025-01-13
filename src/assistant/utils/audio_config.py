import warnings

def configure_audio():
    """Configure audio settings and suppress warnings"""
    warnings.filterwarnings("ignore", category=RuntimeWarning) 