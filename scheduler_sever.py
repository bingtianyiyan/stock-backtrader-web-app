from contextlib import asynccontextmanager
from fastapi import FastAPI
from datetime import date

from internal.tasks.fastapi_add_scheduler_runner import scheduler


# from core.config.configmanager import ConfigContainer
# from core.config.fullconfig import FullConfig
# from core.pkg.scheduler.scheduler_manager import SchedulerManager
#
# schedulerManager = SchedulerManager(ConfigContainer.get_config(FullConfig).scheduler_config)
#
# scheduler = schedulerManager._scheduler
#

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start scheduler (no await needed)
    scheduler.start()
    yield
    # Shutdown scheduler (no await needed)
    scheduler.shutdown()
# 3. Create FastAPI app and mount the admin site immediately
app = FastAPI()

# Assign lifespan after mounting
app.router.lifespan_context = lifespan


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)