import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v0 import create_router

def create_app() -> FastAPI:
    app = FastAPI(
        title="Translation system",
        version="0.1.0",
        docs_url="/documentation",
        swagger_ui_parameters={
            "defaultModelsExpandDepth": -1,
            "displayRequestDuration": 1,
        },
    )

    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    api_router = create_router()
    app.include_router(api_router, prefix="/api/v0", tags=["api", "v0"])

    return app


if __name__ == "__main__":
    uvicorn.run(create_app(), host="127.0.0.1", port=8000, log_level="info")
