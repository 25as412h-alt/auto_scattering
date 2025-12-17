"""
Core Exceptions - ドメイン例外
ビジネスロジックにおける異常系を表現
"""


class AutoScatteringError(Exception):
    """アプリケーション基底例外"""
    pass


class DataLoadError(AutoScatteringError):
    """データ読み込み時のエラー"""
    pass


class AnalysisError(AutoScatteringError):
    """分析処理時のエラー"""
    pass


class ValidationError(AutoScatteringError):
    """データ検証時のエラー"""
    pass


class ConfigurationError(AutoScatteringError):
    """設定ファイル関連のエラー"""
    pass