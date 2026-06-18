from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
async def index() -> HTMLResponse:
    """Стартовая страница с навигацией по API."""
    html = """
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Taro Bot API</title>
        <style>
            * { box-sizing: border-box; margin: 0; padding: 0; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                background: #0f0f14;
                color: #e8e8f0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 2rem;
            }
            .card {
                background: #1a1a24;
                border: 1px solid #2a2a3a;
                border-radius: 16px;
                padding: 2.5rem;
                max-width: 480px;
                width: 100%;
                box-shadow: 0 8px 32px rgba(0,0,0,0.4);
            }
            h1 { font-size: 1.5rem; margin-bottom: 0.25rem; }
            .subtitle { color: #8888a0; font-size: 0.9rem; margin-bottom: 2rem; }
            .links { display: flex; flex-direction: column; gap: 0.75rem; }
            a {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 1rem 1.25rem;
                background: #22222f;
                border: 1px solid #333348;
                border-radius: 10px;
                color: #c8c8e0;
                text-decoration: none;
                transition: background 0.15s, border-color 0.15s;
            }
            a:hover { background: #2a2a3c; border-color: #6b4fa0; color: #fff; }
            .icon { font-size: 1.25rem; }
            .label { font-weight: 500; }
            .desc { font-size: 0.8rem; color: #707090; margin-top: 0.1rem; }
            .text { display: flex; flex-direction: column; }
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🔮 Taro Bot API</h1>
            <p class="subtitle">Выберите, что открыть</p>
            <div class="links">
                <a href="/docs">
                    <span class="icon">📖</span>
                    <div class="text">
                        <span class="label">Swagger UI</span>
                        <span class="desc">Документация и тестирование запросов</span>
                    </div>
                </a>
                <a href="/redoc">
                    <span class="icon">📄</span>
                    <div class="text">
                        <span class="label">ReDoc</span>
                        <span class="desc">Читаемая документация API</span>
                    </div>
                </a>
                <a href="/openapi.json">
                    <span class="icon">{ }</span>
                    <div class="text">
                        <span class="label">OpenAPI JSON</span>
                        <span class="desc">Схема API для интеграций</span>
                    </div>
                </a>
                <a href="/health">
                    <span class="icon">💚</span>
                    <div class="text">
                        <span class="label">Health</span>
                        <span class="desc">Проверка, что сервер работает</span>
                    </div>
                </a>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
