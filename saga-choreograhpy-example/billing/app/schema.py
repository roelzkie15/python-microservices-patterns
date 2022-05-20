
import strawberry

from app.queries import Query

schema = strawberry.Schema(query=Query)
