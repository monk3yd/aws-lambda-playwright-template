from datetime import datetime
from loguru import logger


def main():
    project_name = "fastapi-manager-aws"
    role_name = generate_role_name(project_name)
    logger.debug(f"Role name: {role_name}")

    str_datetime = serialize_datetime(datetime.now())
    logger.debug(f"STR datetime: {str_datetime}")


# Generate role automatic role name from project name
def generate_role_name(project_name):
    role_names = [] 
    names = project_name.split("-")
    for name in names:
        name_part = name.capitalize()
        role_names.append(name_part)

    # Role name
    return "".join(role_names)

# Define a custom function to serialize datetime objects
def serialize_datetime(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError("Type not serializable")

if __name__ == "__main__":
    main()
