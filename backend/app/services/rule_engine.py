import re
import yaml
from typing import List, Dict, Any, Tuple
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

from app.services.grammar_checker import GrammarChecker
from app.services.notation_checker import NotationChecker


class RuleCategory(str, Enum):
    GRAMMAR = "grammar"
    REDUNDANCY = "redundancy"
    FORMATTING = "formatting"
    POLITENESS = "politeness"


@dataclass
class CorrectionResult:
    """校正結果"""
    original_text: str
    corrected_text: str
    start_pos: int
    end_pos: int
    rule_name: str
    category: str
    description: str
    confidence: float = 1.0


@dataclass
class RulePattern:
    """ルールパターン"""
    pattern: str
    replacement: str
    description: str
    type: str = "literal"  # literal or regex
    regex: str = None


@dataclass
class Rule:
    """校正ルール"""
    name: str
    category: str
    priority: int
    patterns: List[RulePattern]


class RuleEngine:
    """ルールベース校正エンジン"""
    
    def __init__(self, rules_dir: str = None):
        self.rules: List[Rule] = []
        self.rules_dir = rules_dir or Path(__file__).parent.parent / "rules"
        self.grammar_checker = GrammarChecker()
        self.notation_checker = NotationChecker()
        self.load_rules()
    
    def load_rules(self) -> None:
        """ルールファイルを読み込み"""
        rules_path = Path(self.rules_dir)
        
        if not rules_path.exists():
            return
        
        for rule_file in rules_path.glob("*.yml"):
            with open(rule_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                self._parse_rules(data)
        
        # 優先度でソート
        self.rules.sort(key=lambda x: x.priority)
    
    def _parse_rules(self, data: Dict[str, Any]) -> None:
        """YAMLデータからルールを解析"""
        rules_data = data.get('rules', {})
        
        for rule_id, rule_config in rules_data.items():
            patterns = []
            
            for pattern_config in rule_config.get('patterns', []):
                pattern = RulePattern(
                    pattern=pattern_config['pattern'],
                    replacement=pattern_config['replacement'],
                    description=pattern_config['description'],
                    type=pattern_config.get('type', 'literal'),
                    regex=pattern_config.get('regex')
                )
                patterns.append(pattern)
            
            rule = Rule(
                name=rule_config['name'],
                category=rule_config['category'],
                priority=rule_config['priority'],
                patterns=patterns
            )
            self.rules.append(rule)
    
    def check_text(self, text: str) -> List[CorrectionResult]:
        """テキストを校正チェック"""
        results = []
        
        # ルールベースチェック
        for rule in self.rules:
            rule_results = self._apply_rule(text, rule)
            results.extend(rule_results)
        
        # 文法チェッカーを使用
        grammar_results = self.grammar_checker.check_grammar(text)
        results.extend(grammar_results)
        
        # 表記統一チェッカーを使用
        notation_results = self.notation_checker.check_notation(text)
        results.extend(notation_results)
        
        return results
    
    def _apply_rule(self, text: str, rule: Rule) -> List[CorrectionResult]:
        """単一ルールを適用"""
        results = []
        
        for pattern in rule.patterns:
            if pattern.type == "literal":
                # 文字列リテラル検索
                start = 0
                while True:
                    pos = text.find(pattern.pattern, start)
                    if pos == -1:
                        break
                    
                    result = CorrectionResult(
                        original_text=pattern.pattern,
                        corrected_text=pattern.replacement,
                        start_pos=pos,
                        end_pos=pos + len(pattern.pattern),
                        rule_name=rule.name,
                        category=rule.category,
                        description=pattern.description
                    )
                    results.append(result)
                    start = pos + 1
            
            elif pattern.type == "regex":
                # 正規表現検索
                regex_pattern = pattern.regex or pattern.pattern
                for match in re.finditer(regex_pattern, text):
                    result = CorrectionResult(
                        original_text=match.group(),
                        corrected_text=pattern.replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name=rule.name,
                        category=rule.category,
                        description=pattern.description
                    )
                    results.append(result)
        
        return results
    
    def apply_corrections(self, text: str, corrections: List[CorrectionResult]) -> str:
        """校正を適用してテキストを修正"""
        # 後ろから修正して位置ずれを防ぐ
        sorted_corrections = sorted(corrections, key=lambda x: x.start_pos, reverse=True)
        
        modified_text = text
        for correction in sorted_corrections:
            before = modified_text[:correction.start_pos]
            after = modified_text[correction.end_pos:]
            modified_text = before + correction.corrected_text + after
        
        return modified_text
    
    def should_apply_ai_processing(self, text: str) -> bool:
        """AI処理が必要かどうかを判定"""
        corrections = self.check_text(text)
        
        # 複雑な文法エラーや文脈依存の問題がある場合はAI処理が必要
        complex_categories = {RuleCategory.GRAMMAR}
        
        for correction in corrections:
            if correction.category in complex_categories:
                return True
        
        # 文章が長い場合（200文字以上）はAI処理推奨
        if len(text) > 200:
            return True
        
        return False