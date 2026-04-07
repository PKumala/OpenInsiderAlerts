from fastapi import APIRouter
from app.db.models import AnalyzedTrade

router = APIRouter(prefix="/filters/meta", tags=["Filters Meta"])


@router.get("/fields")
def get_filterable_fields():

    fields = []

    for column in AnalyzedTrade.__table__.columns:

        col_type = str(column.type)

        if "INTEGER" in col_type or "NUMERIC" in col_type:
            operators = [">", "<", ">=", "<=", "==", "!="]
            input_type = "number"

        elif "BOOLEAN" in col_type:
            operators = ["=="]
            input_type = "boolean"

        else:
            operators = ["==", "!=", "in"]
            input_type = "text"

        fields.append({
            "name": column.name,
            "type": col_type,
            "operators": operators,
            "input": input_type
        })

    return fields
@router.get("/field-values/{field_name}")
def get_field_values(field_name: str):

    enum_map = {
        "ClusterRate": ["A", "B"],
        "BusinessDaysCat": ["A", "B", "C"],
        "InsideCat": ["Inside-Low", "Inside-Mid", "Inside-High"],
        "DiffRate": ["A", "B"],
    }

    return enum_map.get(field_name, [])