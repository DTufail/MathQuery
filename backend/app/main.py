from fastapi import FastAPI


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application instance.
    """
    app = FastAPI(title="Math Query Assistant", version="0.1.0")

    @app.get("/")
    async def root() -> dict[str, str]:
        """Health check endpoint.

        Returns:
            dict[str, str]: Confirmation message that the service is running.
        """
        return {"status": "ok", "service": "math-query-assistant"}

    return app


app = create_app()

