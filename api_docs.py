import asyncio
import json
from typing import Dict, List

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


# Move the app creation and configuration into a function
def create_app():
    app = FastAPI(
        title="Restaurant Management API Documentation",
        description="API Documentation for Restaurant Management System",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()

SERVICES = {
    "User Service": {
        "url": "http://localhost:8001",
        "description": "Quản lý người dùng và xác thực",
        "color": "#4CAF50",
    },
    "Table Service": {
        "url": "http://localhost:8002",
        "description": "Quản lý bàn và đặt bàn",
        "color": "#2196F3",
    },
    "Menu Service": {
        "url": "http://localhost:8003",
        "description": "Quản lý thực đơn và món ăn",
        "color": "#FF9800",
    },
    "Order Service": {
        "url": "http://localhost:8004",
        "description": "Quản lý đơn hàng",
        "color": "#9C27B0",
    },
    "Kitchen Service": {
        "url": "http://localhost:8005",
        "description": "Quản lý bếp và chế biến",
        "color": "#F44336",
    },
    "Payment Service": {
        "url": "http://localhost:8006",
        "description": "Quản lý thanh toán và hóa đơn",
        "color": "#009688",
    },
}


@app.get("/", response_class=HTMLResponse)
async def get_api_docs():
    try:
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Restaurant Management API Documentation</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
            <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
            <style>
                * {
                    margin: 0;
                    padding: 0;
                    box-sizing: border-box;
                    font-family: 'Roboto', sans-serif;
                }
                body {
                    background-color: #f5f5f5;
                    padding: 20px;
                }
                .container {
                    max-width: 1200px;
                    margin: 0 auto;
                }
                .header {
                    background: #fff;
                    padding: 20px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    margin-bottom: 20px;
                }
                .header h1 {
                    color: #333;
                    margin-bottom: 10px;
                }
                .header p {
                    color: #666;
                }
                .services-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 20px;
                    margin-top: 20px;
                }
                .service-card {
                    background: #fff;
                    border-radius: 10px;
                    padding: 20px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }
                .service-card:hover {
                    transform: translateY(-5px);
                }
                .service-header {
                    display: flex;
                    align-items: center;
                    margin-bottom: 15px;
                }
                .service-icon {
                    width: 40px;
                    height: 40px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    margin-right: 12px;
                }
                .service-icon i {
                    color: white;
                    font-size: 20px;
                }
                .service-title {
                    font-size: 18px;
                    font-weight: 500;
                    color: #333;
                }
                .service-description {
                    color: #666;
                    margin-bottom: 15px;
                    line-height: 1.4;
                }
                .service-status {
                    display: flex;
                    align-items: center;
                    color: #4CAF50;
                    font-size: 14px;
                }
                .service-status.offline {
                    color: #f44336;
                }
                .service-status i {
                    margin-right: 5px;
                }
                .swagger-link {
                    display: inline-block;
                    margin-top: 15px;
                    padding: 8px 16px;
                    background-color: #1976D2;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-size: 14px;
                    transition: background-color 0.2s;
                }
                .swagger-link:hover {
                    background-color: #1565C0;
                }
                .service-endpoints {
                    margin-top: 15px;
                    border-top: 1px solid #eee;
                    padding-top: 15px;
                }
                .endpoint {
                    margin-bottom: 8px;
                    font-size: 14px;
                }
                .endpoint-method {
                    display: inline-block;
                    padding: 2px 6px;
                    border-radius: 3px;
                    color: white;
                    font-size: 12px;
                    margin-right: 8px;
                }
                .get { background-color: #61affe; }
                .post { background-color: #49cc90; }
                .put { background-color: #fca130; }
                .delete { background-color: #f93e3e; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Restaurant Management API Documentation</h1>
                    <p>Tài liệu API cho Hệ thống Quản lý Nhà hàng</p>
                </div>
                <div class="services-grid">
        """

        async with httpx.AsyncClient() as client:
            for service_name, service_info in SERVICES.items():
                try:
                    response = await client.get(
                        f"{service_info['url']}/openapi.json", timeout=2.0
                    )
                    service_status = (
                        "online" if response.status_code == 200 else "offline"
                    )
                    swagger_url = f"{service_info['url']}/docs"

                    icon_class = {
                        "User Service": "fas fa-users",
                        "Table Service": "fas fa-chair",
                        "Menu Service": "fas fa-utensils",
                        "Order Service": "fas fa-clipboard-list",
                        "Kitchen Service": "fas fa-kitchen-set",
                        "Payment Service": "fas fa-credit-card",
                    }.get(service_name, "fas fa-cog")

                    endpoints = []
                    if response.status_code == 200:
                        schema = response.json()
                        for path, methods in schema.get("paths", {}).items():
                            for method, _ in methods.items():
                                endpoints.append((method.upper(), path))

                    html_content += f"""
                    <div class="service-card">
                        <div class="service-header">
                            <div class="service-icon" style="background-color: {service_info['color']}">
                                <i class="{icon_class}"></i>
                            </div>
                            <h2 class="service-title">{service_name}</h2>
                        </div>
                        <p class="service-description">{service_info['description']}</p>
                        <div class="service-status {'online' if service_status == 'online' else 'offline'}">
                            <i class="fas fa-circle"></i>
                            {service_status.title()}
                        </div>
                    """

                    if endpoints:
                        html_content += """
                        <div class="service-endpoints">
                        """
                        for method, path in endpoints[:5]:  # Show first 5 endpoints
                            method_class = method.lower()
                            html_content += f"""
                            <div class="endpoint">
                                <span class="endpoint-method {method_class}">{method}</span>
                                <span>{path}</span>
                            </div>
                            """
                        if len(endpoints) > 5:
                            html_content += f"""
                            <div class="endpoint">
                                <span>And {len(endpoints) - 5} more endpoints...</span>
                            </div>
                            """
                        html_content += "</div>"

                    html_content += f"""
                        <a href="{swagger_url}" target="_blank" class="swagger-link">
                            <i class="fas fa-book"></i> View Full Documentation
                        </a>
                    </div>
                    """
                except Exception as e:
                    html_content += f"""
                    <div class="service-card">
                        <div class="service-header">
                            <div class="service-icon" style="background-color: {service_info['color']}">
                                <i class="fas fa-cog"></i>
                            </div>
                            <h2 class="service-title">{service_name}</h2>
                        </div>
                        <p class="service-description">{service_info['description']}</p>
                        <div class="service-status offline">
                            <i class="fas fa-circle"></i>
                            Offline
                        </div>
                        <p style="color: #666; margin-top: 10px;">Service is currently unavailable</p>
                    </div>
                    """

        html_content += """
                </div>
            </div>
            <script>
                // Add any interactive features here
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    print("Please run 'uvicorn api_docs:app --reload' to start the server")
