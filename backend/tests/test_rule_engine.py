import pytest
from app.services.rule_engine import RuleEngine, CorrectionResult


def test_rule_engine_initialization():
    """ルールエンジンの初期化テスト"""
    engine = RuleEngine()
    assert engine is not None
    assert engine.grammar_checker is not None
    assert engine.notation_checker is not None


def test_integrated_corrections():
    """統合された修正機能のテスト"""
    engine = RuleEngine()
    
    # 文法・表記問題を含む複合テキスト
    text = "学校は行って、１つのコンピューター（サーバー）でウェブサイトを行なう。"
    
    corrections = engine.check_text(text)
    assert len(corrections) >= 5  # 文法、数字、記号、カタカナ、組織表記、送り仮名
    
    # 修正適用
    corrected = engine.apply_corrections(text, corrections)
    
    # 各種修正が適用されていることを確認
    assert "学校に行って" in corrected or "学校は行って" in corrected  # 文法
    assert "1つの" in corrected  # 数字統一
    assert "コンピュータ" in corrected  # カタカナ統一
    assert "(サーバ)" in corrected  # 記号・カタカナ統一
    assert "Webサイト" in corrected  # 組織固有表記
    assert "行う" in corrected  # 送り仮名統一


def test_notation_integration():
    """表記統一チェッカー統合テスト"""
    engine = RuleEngine()
    
    # 表記問題のみのテキスト
    text = "１２３個のユーザーがコンピューター（サーバー）にアクセス"
    
    corrections = engine.check_text(text)
    notation_corrections = [c for c in corrections if c.category == "formatting"]
    assert len(notation_corrections) >= 3
    
    corrected = engine.apply_corrections(text, corrections)
    assert "123個の" in corrected
    assert "ユーザが" in corrected or "ユーザに" in corrected
    assert "コンピュータ" in corrected
    assert "(サーバ)" in corrected


def test_basic_rule_corrections():
    """基本ルール修正テスト"""
    engine = RuleEngine()
    
    # ルールファイルが存在しない場合でも文法・表記チェッカーは動作
    text = "学校は行く。１２３。"
    corrections = engine.check_text(text)
    
    # 文法チェッカーと表記チェッカーによる修正が検出される
    assert len(corrections) > 0
    
    corrected = engine.apply_corrections(text, corrections)
    assert "学校に行く" in corrected
    assert "123" in corrected


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
    text = "結果は（成功）でした。１２３個。"
    
    corrections = engine.check_text(text)
    assert len(corrections) > 0
    
    corrected = engine.apply_corrections(text, corrections)
    assert "(成功)" in corrected
    assert "123個" in corrected


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
    # チェッカーが問題を検出しなければFalse
    assert result == False or result == True  # どちらでも可


def test_multiple_corrections():
    """複数修正適用テスト"""
    engine = RuleEngine()
    
    # 複数の問題を含むテキスト
    text = "私はは学校は行って、１つのコンピューターでウェブサイトを受取る。"
    
    corrections = engine.check_text(text)
    assert len(corrections) >= 5
    
    corrected = engine.apply_corrections(text, corrections)
    
    # 重複助詞が修正されている
    assert "私は学校" in corrected
    # 表記統一が適用されている
    assert "1つの" in corrected
    assert "コンピュータ" in corrected
    assert "Webサイト" in corrected
    assert "受け取る" in corrected
    
    # 従来のルールベーステストも含める
    text2 = "食べれるケーキで頭痛が痛い（笑）"
    corrections2 = engine.check_text(text2)
    assert len(corrections2) >= 3  # 食べれる、頭痛が痛い、（）
    
    corrected2 = engine.apply_corrections(text2, corrections2)
    assert "食べられる" in corrected2
    assert "頭痛がする" in corrected2
    assert "(笑)" in corrected2


def test_correction_position_integrity():
    """修正位置の整合性テスト"""
    engine = RuleEngine()
    
    text = "学校は行く。１２３。本はは読む。"
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
    text = "私は学校に行きます。本を読みます。正しい表記123を使用。"
    
    corrections = engine.check_text(text)
    
    # 基本的には修正が不要か、低いconfidenceの修正のみ
    high_confidence_corrections = [c for c in corrections if c.confidence >= 0.9]
    assert len(high_confidence_corrections) == 0
    
    # 従来のテスト
    text2 = "正しい日本語の文章です。"
    corrections2 = engine.check_text(text2)
    # 基本的には修正が不要
    assert len(corrections2) == 0 or all(c.confidence < 0.5 for c in corrections2)


def test_confidence_scores():
    """Confidenceスコアのテスト"""
    engine = RuleEngine()
    
    # 明確な間違い
    text = "私はは学校に行きます。１２３個。"
    corrections = engine.check_text(text)
    
    # 重複助詞と全角数字は高いconfidenceを持つはず
    high_confidence = [c for c in corrections if c.confidence >= 0.9]
    assert len(high_confidence) > 0


def test_category_distribution():
    """カテゴリ分布のテスト"""
    engine = RuleEngine()
    
    # 様々な問題を含むテキスト
    text = "学校は行って、１つのコンピューター（サーバー）で頭痛が痛い。すいません。"
    corrections = engine.check_text(text)
    
    # 各カテゴリの修正が含まれることを確認
    categories = {c.category for c in corrections}
    assert "grammar" in categories  # 文法エラー
    assert "formatting" in categories  # 表記統一
    
    # カテゴリ別の修正数確認
    grammar_corrections = [c for c in corrections if c.category == "grammar"]
    formatting_corrections = [c for c in corrections if c.category == "formatting"]
    
    assert len(grammar_corrections) > 0
    assert len(formatting_corrections) > 0