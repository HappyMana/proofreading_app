import pytest
from app.services.notation_checker import NotationChecker, NotationType


def test_notation_checker_initialization():
    """表記統一チェッカーの初期化テスト"""
    checker = NotationChecker()
    assert checker is not None
    assert len(checker.rules) > 0


def test_number_notation_check():
    """数字表記統一テスト"""
    checker = NotationChecker()
    
    test_cases = [
        ("１２３", "123"),
        ("０点", "0点"),
        ("５つの項目", "5つの項目"),
    ]
    
    for original, expected_part in test_cases:
        corrections = checker.check_numbers(original)
        assert len(corrections) > 0
        
        # 修正適用
        modified = original
        for correction in reversed(corrections):
            before = modified[:correction.start_pos]
            after = modified[correction.end_pos:]
            modified = before + correction.corrected_text + after
        
        # 期待する数字が含まれているかチェック
        assert any(char in modified for char in "0123456789")


def test_punctuation_notation_check():
    """記号表記統一テスト"""
    checker = NotationChecker()
    
    test_cases = [
        ("（括弧）", "(括弧)"),
        ("質問？", "質問?"),
        ("感嘆！", "感嘆!"),
        ("［角括弧］", "[角括弧]"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_punctuation(original)
        assert len(corrections) > 0
        
        # 修正適用
        modified = original
        for correction in reversed(corrections):
            before = modified[:correction.start_pos]
            after = modified[correction.end_pos:]
            modified = before + correction.corrected_text + after
        
        assert expected == modified


def test_katakana_notation_check():
    """カタカナ表記統一テスト"""
    checker = NotationChecker()
    
    test_cases = [
        ("コンピューター", "コンピュータ"),
        ("ユーザー", "ユーザ"),
        ("サーバー", "サーバ"),
        ("データー", "データ"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_katakana(original)
        assert len(corrections) > 0
        assert corrections[0].corrected_text == expected


def test_okurigana_notation_check():
    """送り仮名統一テスト"""
    checker = NotationChecker()
    
    test_cases = [
        ("行なう", "行う"),
        ("受取る", "受け取る"),
        ("取扱い", "取り扱い"),
        ("申込み", "申し込み"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_okurigana(original)
        assert len(corrections) > 0
        assert corrections[0].corrected_text == expected


def test_custom_notation_check():
    """組織固有表記統一テスト"""
    checker = NotationChecker()
    
    test_cases = [
        ("ウェブサイト", "Webサイト"),
        ("ホームページ", "Webサイト"),
        ("ウェブページ", "Webページ"),
        ("Eメール", "メール"),
    ]
    
    for original, expected in test_cases:
        corrections = checker.check_custom_notation(original)
        assert len(corrections) > 0
        assert corrections[0].corrected_text == expected


def test_mixed_notation_check():
    """混在表記統一テスト"""
    checker = NotationChecker()
    
    # 同一文書内で表記が混在している場合
    mixed_text = "ユーザーはサーバにアクセスします。ユーザの情報をサーバーで管理します。"
    corrections = checker.check_mixed_notation(mixed_text)
    
    # 混在が検出されることを確認
    assert len(corrections) > 0


def test_comprehensive_notation_check():
    """包括的表記統一チェックテスト"""
    checker = NotationChecker()
    
    # 複数の表記問題を含むテキスト
    complex_text = "１つのコンピューター（サーバー）でウェブサイトを行なう。"
    
    corrections = checker.check_notation(complex_text)
    
    # 複数の問題が検出されることを確認
    assert len(corrections) >= 4  # 数字、カタカナ、記号、送り仮名、組織表記
    
    # 修正適用
    modified = complex_text
    for correction in sorted(corrections, key=lambda x: x.start_pos, reverse=True):
        before = modified[:correction.start_pos]
        after = modified[correction.end_pos:]
        modified = before + correction.corrected_text + after
    
    # 各種修正が適用されていることを確認
    assert "1つの" in modified  # 数字統一
    assert "コンピュータ" in modified  # カタカナ統一
    assert "(サーバ)" in modified  # 記号・カタカナ統一
    assert "Webサイト" in modified  # 組織固有表記
    assert "行う" in modified  # 送り仮名統一


def test_no_notation_errors():
    """表記エラーがないテキストのテスト"""
    checker = NotationChecker()
    
    correct_text = "正しい表記のテキストです。半角数字123と半角記号()を使用。"
    corrections = checker.check_notation(correct_text)
    
    # 基本的には問題が検出されないか、低いconfidenceの修正のみ
    high_confidence_corrections = [c for c in corrections if c.confidence >= 0.9]
    assert len(high_confidence_corrections) == 0


def test_confidence_scores():
    """Confidenceスコアのテスト"""
    checker = NotationChecker()
    
    # 明確な間違い（全角数字）
    text = "１２３"
    corrections = checker.check_numbers(text)
    
    # 全角数字は高いconfidenceを持つはず
    for correction in corrections:
        assert correction.confidence >= 0.9
    
    # 表記揺れ（カタカナ長音符）
    text2 = "ユーザー"
    corrections2 = checker.check_katakana(text2)
    
    # カタカナ長音符はやや低めのconfidence
    for correction in corrections2:
        assert 0.7 <= correction.confidence < 0.9


def test_rule_types():
    """ルールタイプの分類テスト"""
    checker = NotationChecker()
    
    # 各タイプのルールが存在することを確認
    rule_types = {rule.rule_type for rule in checker.rules}
    
    assert NotationType.NUMBERS in rule_types
    assert NotationType.PUNCTUATION in rule_types
    assert NotationType.KATAKANA in rule_types
    assert NotationType.OKURIGANA in rule_types
    assert NotationType.CUSTOM in rule_types