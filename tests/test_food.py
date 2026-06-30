import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException

from app.food import build_nutrition_prompt, extract_json, guess_image


def test_build_nutrition_prompt_returns():
    prompt = build_nutrition_prompt()
    assert isinstance(prompt, str)
    assert len(prompt) > 0

def test_build_nutrition_prompt_contains_json_structure():
    prompt = build_nutrition_prompt()
    assert '"name"' in prompt
    assert '"nutrition"' in prompt
    assert '"calories"' in prompt
    assert '"confidence"' in prompt

def test_build_nutrition_prompt_contains_enums():
    prompt = build_nutrition_prompt()
    assert "raw" in prompt
    assert "grilled" in prompt
    assert "breakfast" in prompt

def test_extract_json_valid():
    text = '{"name": "burger", "calories": 500}'
    result = extract_json(text)
    assert result == {"name": "burger", "calories": 500}

def test_extract_json_no_braces():
    result = extract_json("Pas de JSON")
    assert result is None

def test_extract_json_invalid_json():
    result = extract_json("{name: burger}")
    assert result is None

def test_extract_json_complex():
    text = json.dumps({
        "name": "Grilled chicken",
        "confidence" : 85,
        "nutrition": {
            "calories": 330,
            "protein": 62.0,
            "carbs": 0.0,
            "fat": 7.2
        }
    })
    result = extract_json(text)
    assert result["name"] == "Grilled chicken"
    assert result["nutrition"]["calories"] == 330

@pytest.mark.asyncio
async def test_guess_image_invalid_content_type():
    mock_file = MagicMock()
    mock_file.content_type = "application/pdf"

    with pytest.raises(HTTPException) as exc_info:
        await guess_image(mock_file)

    assert exc_info.value.status_code == 400

@pytest.mark.asyncio
async def test_guess_image_success():
    mock_file = AsyncMock()
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"fake_image_bytes")

    fake_response_data = {
        "name": "burger",
        "confidence": 90,
        'nutrition': {"calories": 550}
    }

    mock_response = MagicMock()
    mock_response.json.return_value = {
        "response" : json.dumps(fake_response_data)
    }

    mock_response.raise_for_status = MagicMock()

    with patch("app.food.requests.post", return_value=mock_response):
        result = await guess_image(mock_file)

    assert result["status"] == "success"
    assert result["is_working"] == 1
    assert result["data"]["name"] == "burger"

@pytest.mark.asyncio
async def test_guess_image_degraded_when_ollama_unavailable():
    import requests as req

    mock_file = AsyncMock()
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"fake_image_bytes")

    with patch("app.food.requests.post", side_effect=req.exceptions.ConnectionError()):
        result = await guess_image(mock_file)

    assert result["status"] == "degraded"
    assert result["is_working"] == 0
    assert result["data"] is None
    assert "manuellement" in result["message"]

@pytest.mark.asyncio
async def test_guesss_image_degraded_when_json_invalid():
    mock_file = AsyncMock()
    mock_file.content_type = "image/jpeg"
    mock_file.read = AsyncMock(return_value=b"fake_image_bytes")

    mock_response = MagicMock()
    mock_response.json.return_value = {"response": "pas du JSON valide"}
    mock_response.raise_for_status = MagicMock()

    with patch("app.food.requests.post", return_value=mock_response):
        result = await guess_image(mock_file)

    assert result["status"] == "degraded"
    assert result["is_working"] == 0
