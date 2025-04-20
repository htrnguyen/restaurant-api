import asyncio
import json

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Create the FastAPI app instance
app = FastAPI(
    title="Restaurant API Documentation",
    description="Combined API documentation for all microservices",
    version="1.0.0",
)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERVICES = {
    "User Service": "http://localhost:8001",
    "Table Service": "http://localhost:8002",
    "Menu Service": "http://localhost:8003",
    "Order Service": "http://localhost:8004",
    "Kitchen Service": "http://localhost:8005",
    "Payment Service": "http://localhost:8006",
}


@app.get("/", response_class=HTMLResponse)
async def get_combined_docs():
    try:
        # HTML template for combined documentation
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Restaurant API Documentation</title>
            <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.5.0/swagger-ui.css" />
            <script src="https://cdn.jsdelivr.net/npm/swagger-ui-dist@4.5.0/swagger-ui-bundle.js"></script>
            <style>
                body { margin: 0; padding: 20px; }
                #swagger-ui { margin: 0 auto; max-width: 1460px; }
                .topbar { display: none; }
                .scheme-container { display: none; }
                .info { margin: 20px 0; }
                .info .title { color: #3b4151; }
                .servers-title { font-size: 18px; font-weight: bold; margin: 10px 0; }
                .server-item { margin: 5px 0; }
            </style>
        </head>
        <body>
            <div id="swagger-ui"></div>
            <script>
                window.onload = () => {
                    const ui = SwaggerUIBundle({
                        urls: [
                            {url: "/openapi.json", name: "Restaurant API"},
                        ],
                        dom_id: '#swagger-ui',
                        deepLinking: true,
                        presets: [
                            SwaggerUIBundle.presets.apis,
                            SwaggerUIBundle.SwaggerUIStandalonePreset
                        ],
                        layout: "BaseLayout",
                        defaultModelsExpandDepth: -1,
                        docExpansion: 'list',
                        filter: true,
                        tagsSorter: 'alpha'
                    });
                };
            </script>
        </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/openapi.json")
async def get_openapi_schema():
    try:
        combined_schema = {
            "openapi": "3.0.0",
            "info": {
                "title": "Restaurant API Documentation",
                "description": "Combined API documentation for all microservices",
                "version": "1.0.0",
            },
            "servers": [],
            "paths": {},
            "components": {"schemas": {}},
            "tags": [],
        }

        async with httpx.AsyncClient() as client:
            tasks = []
            for service_name, base_url in SERVICES.items():
                tasks.append(client.get(f"{base_url}/openapi.json"))

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for service_name, response in zip(SERVICES.keys(), responses):
                if isinstance(response, Exception):
                    print(f"Error fetching {service_name} schema: {str(response)}")
                    continue

                if response.status_code == 200:
                    service_schema = response.json()

                    # Add server
                    combined_schema["servers"].append(
                        {"url": SERVICES[service_name], "description": service_name}
                    )

                    # Add tag for the service
                    combined_schema["tags"].append(
                        {
                            "name": service_name,
                            "description": f"APIs from {service_name}",
                        }
                    )

                    # Add paths with service tag
                    for path, path_item in service_schema.get("paths", {}).items():
                        combined_path = (
                            f"/{service_name.lower().replace(' ', '-')}{path}"
                        )
                        # Add service tag to each operation
                        for operation in path_item.values():
                            if "tags" not in operation:
                                operation["tags"] = []
                            operation["tags"].append(service_name)
                        combined_schema["paths"][combined_path] = path_item

                    # Add components/schemas with service prefix
                    service_schemas = service_schema.get("components", {}).get(
                        "schemas", {}
                    )
                    for schema_name, schema in service_schemas.items():
                        prefixed_name = f"{service_name.replace(' ', '')}{schema_name}"
                        combined_schema["components"]["schemas"][prefixed_name] = schema

        return combined_schema

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Move the server startup code to a separate file
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api_docs:app", host="127.0.0.1", port=8000, reload=True)
