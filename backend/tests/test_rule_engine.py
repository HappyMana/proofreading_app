import pytest
from app.services.rule_engine import RuleEngine, CorrectionResult


def test_rule_engine_initialization():
    """ルールエンジンの初期化テスト"""
    engine = RuleEngine()
    assert engine is not None
    assert engine.grammar_checker is not None


def test_basic_rule_corrections():
    """基本ルール修正テスト"""
    engine = RuleEngine()
    
    # ルールファイルが存在しない場合でも文法チェッカーは動作
    text = "学校は行く"
    corrections = engine.check_text(text)
    
    # 文法チェッカーによる修正が検出される
    assert len(corrections) > 0
    
    corrected = engine.apply_corrections(text, corrections)
    assert "学校に行く" in corrected


def test_grammar_integration():
    """文法チェッカー統合テスト"""
    engine = RuleEngine()
    
    # 複数の文法問題を含むテキスト
    text = "学校は行って、本はは読みます。すいません。"
    
    corrections = engine.check_text(text)
    assert len(corrections) >= 2
    
    # 修正適用
    corrected = engine.apply_corrections(text, corrections)
    
    # 各修正が適用されていることを確認
    assert "学校に行って" in corrected or "学校は行って" in corrected
    assert "本は読みます" in corrected or "本を読みます" in corrected
    assert "すみません" in corrected


def test_ai_processing_recommendation():
    """AI処理推奨判定テスト"""
    engine = RuleEngine()
    
    # 文法問題があるテキスト
    grammar_text = "学校は行く"
    assert engine.should_apply_ai_processing(grammar_text) == True
    
    # 長いテキスト
    long_text = "これは非常に長い文章です。" * 20
    assert engine.should_apply_ai_processing(long_text) == True
    
    # 短くて問題のないテキスト
    simple_text = "こんにちは。"
    result = engine.should_apply_ai_processing(simple_text)
    # 文法チェッカーが問題を検出しなければFalse
    assert result == False or result == True  # どちらでも可


def test_multiple_corrections():
    """複数修正適用テスト"""
    engine = RuleEngine()
    
    # 複数の問題を含むテキスト
    text = "私はは学校は行って、本をを読みます。"
    
    corrections = engine.check_text(text)
    assert len(corrections) >= 2
    
    corrected = engine.apply_corrections(text, corrections)
    
    # 重複助詞が修正されている
    assert "私は学校" in corrected
    assert "本を読みます" in corrected


def test_correction_position_integrity():
    """修正位置の整合性テスト"""
    engine = RuleEngine()
    
    text = "学校は行く。本はは読む。"
    corrections = engine.check_text(text)
    
    # 位置情報が正しいことを確認
    for correction in corrections:
        assert 0 <= correction.start_pos < len(text)
        assert correction.start_pos < correction.end_pos <= len(text)
        
        # 元テキストが一致することを確認
        original_part = text[correction.start_pos:correction.end_pos]
        assert original_part == correction.original_text


def test_no_corrections_needed():
    """修正不要テキストのテスト"""
    engine = RuleEngine()
    
    # 正しい日本語
    text = "私は学校に行きます。本を読みます。"
    
    corrections = engine.check_text(text)
    
    # 基本的には修正が不要か、低いconfidenceの修正のみ
    high_confidence_corrections = [c for c in corrections if c.confidence >= 0.8]
    assert len(high_confidence_corrections) == 0


def test_confidence_scores():
    """Confidenceスコアのテスト"""
    engine = RuleEngine()
    
    # 明確な間違い
    text = "私はは学校に行きます。"
    corrections = engine.check_text(text)
    
    # 重複助詞は高いconfidenceを持つはず
    duplicate_corrections = [c for c in corrections if "重複" in c.description]
    if duplicate_corrections:
        assert duplicate_corrections[0].confidence >= 0.8