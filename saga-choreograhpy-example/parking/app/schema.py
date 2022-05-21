
import strawberry

from app.queries import Query
from app.mutations import Mutation

schema = strawberry.Schema(query=Query, mutation=Mutation)
