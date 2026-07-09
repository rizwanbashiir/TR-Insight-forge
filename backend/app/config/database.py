from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config.settings import settings

# Compatibility patch for Motor 3.7+ with Beanie
if not callable(getattr(AsyncIOMotorClient, "append_metadata", None)):
    AsyncIOMotorClient.append_metadata = lambda self, *args, **kwargs: self.delegate.append_metadata(*args, **kwargs)

# Global motor client instance
client: AsyncIOMotorClient = None

async def init_db():
    global client
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.MONGODB_DB_NAME]

    from app.models.organizations import Organization
    from app.models.users import User
    from app.models.subscriptions import Subscription
    from app.models.uploaded_file import UploadedFile
    from app.models.raw_data_row import RawDataRow
    from app.models.processed_dataset import ProcessedDataset
    from app.models.ai_insight import AIInsight
    from app.models.forecast_result import ForecastResult
    from app.models.segment_result import SegmentResult

    await init_beanie(
        database=db,
        document_models=[
            Organization,
            User,
            Subscription,
            UploadedFile,
            RawDataRow,
            ProcessedDataset,
            AIInsight,
            ForecastResult,
            SegmentResult,
        ],
    )

def get_db():
    """
    Dependency helper returning the async MongoDB database instance.
    """
    if client is None:
        return None
    return client[settings.MONGODB_DB_NAME]