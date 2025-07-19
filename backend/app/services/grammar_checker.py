import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

try:
    import MeCab
except ImportError:
    MeCab = None

from app.services.rule_engine import CorrectionResult


class ParticleType(str, Enum):
    SUBJECT = "は"  # 主語
    OBJECT = "を"   # 目的語
    DIRECTION = "に"  # 方向
    LOCATION = "で"  # 場所
    TOPIC = "は"    # 話題


@dataclass
class MorphemeInfo:
    """形態素情報"""
    surface: str      # 表層形
    pos: str         # 品詞
    pos_detail: str  # 品詞詳細
    base_form: str   # 基本形
    reading: str     # 読み


class GrammarChecker:
    """文法チェッカー"""
    
    def __init__(self):
        try:
            if MeCab:
                self.mecab = MeCab.Tagger("-Ochasen")
            else:
                self.mecab = None
        except Exception:
            # MeCabが利用できない場合のフォールバック
            self.mecab = None
            print("Warning: MeCab not available, using simplified grammar check")
    
    def analyze_morphemes(self, text: str) -> List[MorphemeInfo]:
        """形態素解析"""
        if not self.mecab:
            return []
        
        result = []
        lines = self.mecab.parse(text).strip().split('\n')
        
        for line in lines:
            if line == 'EOS':
                break
            
            parts = line.split('\t')
            if len(parts) >= 4:
                surface = parts[0]
                pos_info = parts[1].split('-')
                pos = pos_info[0] if pos_info else ""
                pos_detail = pos_info[1] if len(pos_info) > 1 else ""
                base_form = parts[2] if len(parts) > 2 else surface
                reading = parts[3] if len(parts) > 3 else surface
                
                result.append(MorphemeInfo(
                    surface=surface,
                    pos=pos,
                    pos_detail=pos_detail,
                    base_form=base_form,
                    reading=reading
                ))
        
        return result
    
    def check_particle_usage(self, text: str) -> List[CorrectionResult]:
        """助詞の誤用をチェック"""
        corrections = []
        
        # 簡単な助詞誤用パターンをチェック
        particle_patterns = [
            # (誤用パターン, 正しい表現, 説明)
            (r'学校は行く', '学校に行く', '「〜は行く」→「〜に行く」'),
            (r'本は読む', '本を読む', '「〜は読む」→「〜を読む」'),
            (r'友達は会う', '友達に会う', '「〜は会う」→「〜に会う」'),
            (r'テレビは見る', 'テレビを見る', '「〜は見る」→「〜を見る」'),
        ]
        
        for pattern, replacement, description in particle_patterns:
            for match in re.finditer(pattern, text):
                corrections.append(CorrectionResult(
                    original_text=match.group(),
                    corrected_text=replacement,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    rule_name="助詞誤用修正",
                    category="grammar",
                    description=description,
                    confidence=0.8
                ))
        
        return corrections
    
    def check_style_consistency(self, text: str) -> List[CorrectionResult]:
        """文体の統一をチェック"""
        corrections = []
        
        # である調とですます調の混在をチェック
        dearu_pattern = r'である[。．]'
        desu_pattern = r'です[。．]|ます[。．]'
        
        dearu_matches = list(re.finditer(dearu_pattern, text))
        desu_matches = list(re.finditer(desu_pattern, text))
        
        if dearu_matches and desu_matches:
            # 混在している場合、より多い方に統一を提案
            if len(desu_matches) > len(dearu_matches):
                # ですます調に統一
                for match in dearu_matches:
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text="です。",
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="文体統一",
                        category="grammar",
                        description="ですます調に統一",
                        confidence=0.7
                    ))
            else:
                # である調に統一
                for match in desu_matches:
                    if 'です' in match.group():
                        replacement = 'である。'
                    else:  # ます
                        replacement = 'る。'
                    
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="文体統一",
                        category="grammar",
                        description="である調に統一",
                        confidence=0.7
                    ))
        
        return corrections
    
    def check_duplicate_particles(self, text: str) -> List[CorrectionResult]:
        """重複助詞をチェック"""
        corrections = []
        
        duplicate_patterns = [
            (r'はは', 'は', '助詞「は」の重複'),
            (r'をを', 'を', '助詞「を」の重複'),
            (r'でで', 'で', '助詞「で」の重複'),
            (r'にに', 'に', '助詞「に」の重複'),
            (r'のの', 'の', '助詞「の」の重複'),
        ]
        
        for pattern, replacement, description in duplicate_patterns:
            for match in re.finditer(pattern, text):
                corrections.append(CorrectionResult(
                    original_text=match.group(),
                    corrected_text=replacement,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    rule_name="重複助詞修正",
                    category="grammar",
                    description=description,
                    confidence=0.9
                ))
        
        return corrections
    
    def check_keigo_usage(self, text: str) -> List[CorrectionResult]:
        """敬語の誤用をチェック"""
        corrections = []
        
        keigo_patterns = [
            (r'すいません', 'すみません', '正しい謝罪表現'),
            (r'させて頂く', 'させていただく', '敬語表現の修正'),
            (r'させて頂き', 'させていただき', '敬語表現の修正'),
            (r'させて頂いて', 'させていただいて', '敬語表現の修正'),
        ]
        
        for pattern, replacement, description in keigo_patterns:
            for match in re.finditer(pattern, text):
                corrections.append(CorrectionResult(
                    original_text=match.group(),
                    corrected_text=replacement,
                    start_pos=match.start(),
                    end_pos=match.end(),
                    rule_name="敬語修正",
                    category="grammar",
                    description=description,
                    confidence=0.8
                ))
        
        return corrections
    
    def check_modifier_relations(self, text: str) -> List[CorrectionResult]:
        """修飾語関係をチェック"""
        corrections = []
        
        # 「大きい」+名詞のパターンチェック
        modifier_patterns = [
            (r'大きい犬', '大きな犬', '「大きい」→「大きな」（連体修飾）'),
            (r'小さい家', '小さな家', '「小さい」→「小さな」（連体修飾）'),
            (r'新しい町', '新しい町', '正しい修飾関係'),  # チェックのみ
        ]
        
        for pattern, replacement, description in modifier_patterns:
            if pattern != replacement:  # 修正が必要な場合のみ
                for match in re.finditer(pattern, text):
                    corrections.append(CorrectionResult(
                        original_text=match.group(),
                        corrected_text=replacement,
                        start_pos=match.start(),
                        end_pos=match.end(),
                        rule_name="修飾語修正",
                        category="grammar",
                        description=description,
                        confidence=0.7
                    ))
        
        return corrections
    
    def check_grammar(self, text: str) -> List[CorrectionResult]:
        """包括的な文法チェック"""
        all_corrections = []
        
        # 各種チェックを実行
        all_corrections.extend(self.check_particle_usage(text))
        all_corrections.extend(self.check_style_consistency(text))
        all_corrections.extend(self.check_duplicate_particles(text))
        all_corrections.extend(self.check_keigo_usage(text))
        all_corrections.extend(self.check_modifier_relations(text))
        
        # 重複を除去（同じ位置の修正）
        unique_corrections = []
        seen_positions = set()
        
        for correction in all_corrections:
            pos_key = (correction.start_pos, correction.end_pos)
            if pos_key not in seen_positions:
                unique_corrections.append(correction)
                seen_positions.add(pos_key)
        
        return unique_corrections