
import strawberry

from app.mutations import Mutation
from app.queries import Query

schema = strawberry.Schema(query=Query, mutation=Mutation)
