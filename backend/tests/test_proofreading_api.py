import pytest
from fastapi.testclient import TestClient


def test_proofreading_check_endpoint(client: TestClient):
    """校正チェックエンドポイントテスト"""
    response = client.post(
        "/api/v1/proofreading/check",
        json={
            "text": "食べれるケーキ",
            "apply_corrections": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "original_text" in data
    assert "corrected_text" in data
    assert "corrections" in data
    assert "ai_processing_recommended" in data
    assert len(data["corrections"]) > 0


def test_proofreading_with_corrections(client: TestClient):
    """校正適用エンドポイントテスト"""
    response = client.post(
        "/api/v1/proofreading/check",
        json={
            "text": "食べれるケーキで頭痛が痛い",
            "apply_corrections": True
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "食べられる" in data["corrected_text"]
    assert "頭痛がする" in data["corrected_text"]


def test_rules_endpoint(client: TestClient):
    """ルール一覧エンドポイントテスト"""
    response = client.get("/api/v1/proofreading/rules")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "rules" in data
    assert len(data["rules"]) > 0
    
    # ルール情報の構造確認
    rule = data["rules"][0]
    assert "name" in rule
    assert "category" in rule
    assert "priority" in rule
    assert "pattern_count" in rule


def test_proofreading_health_endpoint(client: TestClient):
    """ルールエンジンヘルスチェックテスト"""
    response = client.get("/api/v1/proofreading/health")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "rules_loaded" in data
    assert "engine_version" in data


def test_empty_text(client: TestClient):
    """空文字テストタ"""
    response = client.post(
        "/api/v1/proofreading/check",
        json={
            "text": "",
            "apply_corrections": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["original_text"] == ""
    assert len(data["corrections"]) == 0


def test_long_text(client: TestClient):
    """長文テスト"""
    long_text = "これは長い文章のテストです。" * 50
    
    response = client.post(
        "/api/v1/proofreading/check",
        json={
            "text": long_text,
            "apply_corrections": False
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["ai_processing_recommended"] == True