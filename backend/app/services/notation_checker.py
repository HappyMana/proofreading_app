import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from app.services.rule_engine import CorrectionResult


class NotationType(str, Enum):
    NUMBERS = "numbers"
    PUNCTUATION = "punctuation"
    KATAKANA = "katakana"
    OKURIGANA = "okurigana"
    CUSTOM = "custom"


@dataclass
class NotationRule:
    """表記統一ルール"""
    pattern: str
    replacement: str
    description: str
    rule_type: NotationType
    confidence: float = 0.9


class NotationChecker:
    """表記統一チェッカー"""
    
    def __init__(self):
        self.rules = self._initialize_rules()
    
    def _initialize_rules(self) -> List[NotationRule]:
        """表記統一ルールを初期化"""
        rules = []
        
        # 全角数字→半角数字
        zenkaku_numbers = "０１２３４５６７８９"
        hankaku_numbers = "0123456789"
        for z, h in zip(zenkaku_numbers, hankaku_numbers):
            rules.append(NotationRule(
                pattern=z,
                replacement=h,
                description=f"全角数字「{z}」を半角「{h}」に",
                rule_type=NotationType.NUMBERS,
                confidence=0.95
            ))
        
        # 記号統一
        punctuation_rules = [
            ("（", "(", "全角括弧を半角に"),
            ("）", ")", "全角括弧を半角に"),
            ("［", "[", "全角角括弧を半角に"),
            ("］", "]", "全角角括弧を半角に"),
            ("！", "!", "全角感嘆符を半角に"),
            ("？", "?", "全角疑問符を半角に"),
            ("：", ":", "全角コロンを半角に"),
            ("；", ";", "全角セミコロンを半角に"),
        ]
        
        for original, replacement, description in punctuation_rules:
            rules.append(NotationRule(
                pattern=original,
                replacement=replacement,
                description=description,
                rule_type=NotationType.PUNCTUATION,
                confidence=0.9
            ))
        
        # カタカナ長音符統一
        katakana_rules = [
            ("コンピューター", "コンピュータ", "長音符統一"),
            ("システムー", "システム", "語尾長音符削除"),
            ("データー", "データ", "語尾長音符削除"),
            ("ユーザー", "ユーザ", "語尾長音符削除"),
            ("サーバー", "サーバ", "語尾長音符削除"),
            ("プリンター", "プリンタ", "語尾長音符削除"),
            ("フォルダー", "フォルダ", "語尾長音符削除"),
            ("ブラウザー", "ブラウザ", "語尾長音符削除"),
        ]
        
        for original, replacement, description in katakana_rules:
            rules.append(NotationRule(
                pattern=original,
                replacement=replacement,
                description=description,
                rule_type=NotationType.KATAKANA,
                confidence=0.8
            ))
        
        # 送り仮名統一
        okurigana_rules = [
            ("行なう", "行う", "送り仮名統一"),
            ("行なって", "行って", "送り仮名統一"),
            ("行なった", "行った", "送り仮名統一"),
            ("受取る", "受け取る", "送り仮名統一"),
            ("受取って", "受け取って", "送り仮名統一"),
            ("受取った", "受け取った", "送り仮名統一"),
            ("取扱い", "取り扱い", "送り仮名統一"),
            ("申込み", "申し込み", "送り仮名統一"),
        ]
        
        for original, replacement, description in okurigana_rules:
            rules.append(NotationRule(
                pattern=original,
                replacement=replacement,
                description=description,
                rule_type=NotationType.OKURIGANA,
                confidence=0.85
            ))
        
        # 組織固有表記
        custom_rules = [
            ("ウェブサイト", "Webサイト", "サービス名表記統一"),
            ("ホームページ", "Webサイト", "サービス名表記統一"),
            ("ウェブページ", "Webページ", "サービス名表記統一"),
            ("Eメール", "メール", "表記統一"),
            ("イーメール", "メール", "表記統一"),
        ]
        
        for original, replacement, description in custom_rules:
            rules.append(NotationRule(
                pattern=original,
                replacement=replacement,
                description=description,
                rule_type=NotationType.CUSTOM,
                confidence=0.7
            ))
        
        return rules
    
    def check_numbers(self, text: str) -> List[CorrectionResult]:
        """数字表記をチェック"""
        corrections = []
        
        for rule in self.rules:
            if rule.rule_type == NotationType.NUMBERS:
                for match in re.finditer(re.escape(rule.pattern), text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=rule.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="数字表記統一",
                        category="formatting",
                        description=rule.description,
                        confidence=rule.confidence
                    ))
        
        return corrections
    
    def check_punctuation(self, text: str) -> List[CorrectionResult]:
        """記号表記をチェック"""
        corrections = []
        
        for rule in self.rules:
            if rule.rule_type == NotationType.PUNCTUATION:
                for match in re.finditer(re.escape(rule.pattern), text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=rule.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="記号表記統一",
                        category="formatting",
                        description=rule.description,
                        confidence=rule.confidence
                    ))
        
        return corrections
    
    def check_katakana(self, text: str) -> List[CorrectionResult]:
        """カタカナ表記をチェック"""
        corrections = []
        
        for rule in self.rules:
            if rule.rule_type == NotationType.KATAKANA:
                for match in re.finditer(re.escape(rule.pattern), text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=rule.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="カタカナ表記統一",
                        category="formatting",
                        description=rule.description,
                        confidence=rule.confidence
                    ))
        
        return corrections
    
    def check_okurigana(self, text: str) -> List[CorrectionResult]:
        """送り仮名をチェック"""
        corrections = []
        
        for rule in self.rules:
            if rule.rule_type == NotationType.OKURIGANA:
                for match in re.finditer(re.escape(rule.pattern), text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=rule.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="送り仮名統一",
                        category="formatting",
                        description=rule.description,
                        confidence=rule.confidence
                    ))
        
        return corrections
    
    def check_custom_notation(self, text: str) -> List[CorrectionResult]:
        """組織固有表記をチェック"""
        corrections = []
        
        for rule in self.rules:
            if rule.rule_type == NotationType.CUSTOM:
                for match in re.finditer(re.escape(rule.pattern), text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=rule.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="組織固有表記統一",
                        category="formatting",
                        description=rule.description,
                        confidence=rule.confidence
                    ))
        
        return corrections
    
    def check_mixed_notation(self, text: str) -> List[CorrectionResult]:
        """混在表記をチェック"""
        corrections = []
        
        # 同一文書内での表記揺れをチェック
        # 例: "ユーザー"と"ユーザ"が混在している場合
        
        notation_pairs = [
            ("ユーザー", "ユーザ"),
            ("サーバー", "サーバ"),
            ("データー", "データ"),
            ("コンピューター", "コンピュータ"),
        ]
        
        for long_form, short_form in notation_pairs:
            long_matches = list(re.finditer(re.escape(long_form), text))
            short_matches = list(re.finditer(re.escape(short_form), text))
            
            # 両方存在する場合は統一を提案
            if long_matches and short_matches:
                # より少ない方を多い方に統一
                if len(long_matches) < len(short_matches):
                    # 長音あり形式を短形式に統一
                    for match in long_matches:
                        corrections.append(CorrectionResult(
                            original_text=match.group(),
                            corrected_text=short_form,
                            start_pos=match.start(),
                            end_pos=match.end(),
                            rule_name="表記統一",
                            category="formatting",
                            description=f"文書内統一（{short_form}に統一）",
                            confidence=0.6
                        ))
        
        return corrections
    
    def check_notation(self, text: str) -> List[CorrectionResult]:
        """包括的な表記統一チェック"""
        all_corrections = []
        
        # 各種チェックを実行
        all_corrections.extend(self.check_numbers(text))
        all_corrections.extend(self.check_punctuation(text))
        all_corrections.extend(self.check_katakana(text))
        all_corrections.extend(self.check_okurigana(text))
        all_corrections.extend(self.check_custom_notation(text))
        all_corrections.extend(self.check_mixed_notation(text))
        
        # 重複を除去（同じ位置の修正）
        unique_corrections = []
        seen_positions = set()
        
        for correction in all_corrections:
            pos_key = (correction.start_pos, correction.end_pos)
            if pos_key not in seen_positions:
                unique_corrections.append(correction)
                seen_positions.add(pos_key)
        
        return unique_corrections