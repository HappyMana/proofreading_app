from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

from app.services.rule_engine import RuleEngine, CorrectionResult


router = APIRouter(prefix="/api/v1/proofreading", tags=["proofreading"])


class ProofreadingRequest(BaseModel):
    text: str
    apply_corrections: bool = False


class CorrectionResponse(BaseModel):
    original_text: str
    corrected_text: str
    start_pos: int
    end_pos: int
    rule_name: str
    category: str
    description: str
    confidence: float


class ProofreadingResponse(BaseModel):
    original_text: str
    corrected_text: str
    corrections: List[CorrectionResponse]
    ai_processing_recommended: bool


# ルールエンジンのインスタンスを作成
rule_engine = RuleEngine()


@router.post("/check", response_model=ProofreadingResponse)
async def check_text(request: ProofreadingRequest):
    """テキストの校正チェック"""
    try:
        # ルールベースチェック実行
        corrections = rule_engine.check_text(request.text)
        
        # 修正を適用するかどうか
        corrected_text = request.text
        if request.apply_corrections:
            corrected_text = rule_engine.apply_corrections(request.text, corrections)
        
        # AI処理が推奨されるかチェック
        ai_recommended = rule_engine.should_apply_ai_processing(request.text)
        
        # レスポンス形式に変換
        correction_responses = [
            CorrectionResponse(
                original_text=c.original_text,
                corrected_text=c.corrected_text,
                start_pos=c.start_pos,
                end_pos=c.end_pos,
                rule_name=c.rule_name,
                category=c.category,
                description=c.description,
                confidence=c.confidence
            )
            for c in corrections
        ]
        
        return ProofreadingResponse(
            original_text=request.text,
            corrected_text=corrected_text,
            corrections=correction_responses,
            ai_processing_recommended=ai_recommended
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"校正処理中にエラーが発生しました: {str(e)}")


@router.get("/rules")
async def get_rules():
    """利用可能なルール一覧を取得"""
    try:
        rules_info = []
        for rule in rule_engine.rules:
            rules_info.append({
                "name": rule.name,
                "category": rule.category,
                "priority": rule.priority,
                "pattern_count": len(rule.patterns)
            })
        
        return {"rules": rules_info}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ルール取得中にエラーが発生しました: {str(e)}")


@router.get("/health")
async def health_check():
    """ルールエンジンのヘルスチェック"""
    return {
        "status": "healthy",
        "rules_loaded": len(rule_engine.rules),
        "engine_version": "1.0.0"
    }