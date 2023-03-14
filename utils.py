from passlib.context import CryptContext


def create_tree(nodes=[], parent_id=None, config={}):
    '''
        nodes       - List of flat nodes to be converted into the tree
        parentId    - Parent node id to collect children
        config      - Dict with the keys to dynamically construct the tree
    '''
    return list([{**i, config["children_path"]: create_tree(nodes, i[config["key"]], config)} for i in nodes if
                 i[config["parentKey"]] == parent_id])


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
