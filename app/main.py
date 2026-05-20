from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.session import AsyncSessionLocal
from app.db.seed import seed_products
from app.api.routes import health, products, orders, tracking, admin, config

setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    async with AsyncSessionLocal() as db:
        await seed_products(db)
    yield


app = FastAPI(
    title="NAJD API",
    description="NAJD night skincare storefront API — cosmetics-facing copy",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list + ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", include_in_schema=False)
async def storefront() -> FileResponse:
    return FileResponse("static/index.html")

@app.get("/product.html", include_in_schema=False)
async def product_page() -> FileResponse:
    return FileResponse("static/product.html")

app.include_router(health.router)
app.include_router(config.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(tracking.router)
app.include_router(admin.router)
