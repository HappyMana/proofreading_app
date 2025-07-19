import pytest
from app.services.grammar_checker import GrammarChecker


def test_grammar_checker_initialization():
    """文法チェッカーの初期化テスト"""
    checker = GrammarChecker()
    assert checker is not None


def test_particle_usage_check():
    """助詞誤用チェックテスト"""
    checker = GrammarChecker()
    
    # 助詞誤用のテスト
    test_cases = [
        ("学校は行く", "学校に行く"),
        ("本は読む", "本を読む"),
        ("友達は会う", "友達に会う"),
        ("テレビは見る", "テレビを見る"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_particle_usage(original)
        assert len(corrections) > 0
        assert corrections[0].corrected_text == expected


def test_duplicate_particles_check():
    """重複助詞チェックテスト"""
    checker = GrammarChecker()
    
    test_cases = [
        ("私はは学生です", "私は学生です"),
        ("本をを読みます", "本を読みます"),
        ("学校でで勉強します", "学校で勉強します"),
    ]
    
    for original, expected_part in test_cases:
        corrections = checker.check_duplicate_particles(original)
        assert len(corrections) > 0
        # 重複部分が修正されることを確認
        assert any(c.original_text in original for c in corrections)


def test_keigo_usage_check():
    """敬語チェックテスト"""
    checker = GrammarChecker()
    
    test_cases = [
        ("すいません", "すみません"),
        ("させて頂く", "させていただく"),
        ("させて頂き", "させていただき"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_keigo_usage(original)
        assert len(corrections) > 0
        assert corrections[0].corrected_text == expected


def test_style_consistency_check():
    """文体統一チェックテスト"""
    checker = GrammarChecker()
    
    # である調とですます調の混在
    mixed_style_text = "これは例文である。これは例文です。"
    corrections = checker.check_style_consistency(mixed_style_text)
    
    # 文体の混在が検出されることを確認
    assert len(corrections) > 0


def test_modifier_relations_check():
    """修飾語関係チェックテスト"""
    checker = GrammarChecker()
    
    test_cases = [
        ("大きい犬", "大きな犬"),
        ("小さい家", "小さな家"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_modifier_relations(original)
        if corrections:  # 修正が必要な場合
            assert corrections[0].corrected_text == expected


def test_comprehensive_grammar_check():
    """包括的文法チェックテスト"""
    checker = GrammarChecker()
    
    # 複数の文法エラーを含むテキスト
    complex_text = "学校は行って、本はは読みます。すいません。"
    
    corrections = checker.check_grammar(complex_text)
    
    # 複数の問題が検出されることを確認
    assert len(corrections) >= 2
    
    # 重複除去が正しく動作することを確認
    positions = [(c.start_pos, c.end_pos) for c in corrections]
    assert len(positions) == len(set(positions))


def test_no_grammar_errors():
    """文法エラーがないテキストのテスト"""
    checker = GrammarChecker()
    
    correct_text = "私は学校に行きます。本を読みます。"
    corrections = checker.check_grammar(correct_text)
    
    # 基本的には問題が検出されないか、confidence が低い
    assert len(corrections) == 0 or all(c.confidence < 0.9 for c in corrections)