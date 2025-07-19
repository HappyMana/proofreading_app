import pytest
from app.services.rule_engine import RuleEngine, CorrectionResult


def test_rule_engine_initialization():
    """ルールエンジンの初期化テスト"""
    engine = RuleEngine()
    assert len(engine.rules) > 0


def test_ra_nuki_correction():
    """ら抜き言葉修正テスト"""
    engine = RuleEngine()
    text = "このケーキは食べれる"
    
    corrections = engine.check_text(text)
    assert len(corrections) > 0
    
    # 修正適用
    corrected = engine.apply_corrections(text, corrections)
    assert "食べられる" in corrected


def test_duplication_correction():
    """重複表現修正テスト"""
    engine = RuleEngine()
    text = "頭痛が痛いです"
    
    corrections = engine.check_text(text)
    assert len(corrections) > 0
    
    corrected = engine.apply_corrections(text, corrections)
    assert "頭痛がする" in corrected


def test_formatting_correction():
    """表記統一テスト"""
    engine = RuleEngine()
    text = "結果は（成功）でした"
    
    corrections = engine.check_text(text)
    assert len(corrections) > 0
    
    corrected = engine.apply_corrections(text, corrections)
    assert "(成功)" in corrected


def test_ai_processing_recommendation():
    """AI処理推奨判定テスト"""
    engine = RuleEngine()
    
    # 短い文章、単純な修正
    short_text = "問題ない"
    assert not engine.should_apply_ai_processing(short_text)
    
    # 長い文章
    long_text = "これは非常に長い文章で、複雑な文法構造や文脈に依存する表現が含まれている可能性があります。" * 3
    assert engine.should_apply_ai_processing(long_text)


def test_multiple_corrections():
    """複数修正適用テスト"""
    engine = RuleEngine()
    text = "食べれるケーキで頭痛が痛い（笑）"
    
    corrections = engine.check_text(text)
    assert len(corrections) >= 3  # 食べれる、頭痛が痛い、（）
    
    corrected = engine.apply_corrections(text, corrections)
    assert "食べられる" in corrected
    assert "頭痛がする" in corrected
    assert "(笑)" in corrected


def test_no_corrections_needed():
    """修正不要テキストのテスト"""
    engine = RuleEngine()
    text = "正しい日本語の文章です。"
    
    corrections = engine.check_text(text)
    # 基本的には修正が不要
    assert len(corrections) == 0 or all(c.confidence < 0.5 for c in corrections)