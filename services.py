import database as _db
from fastapi import security
import sqlalchemy.orm as orm
from models import UserModel, PostModel
import schemas
import email_validator
import fastapi
import passlib.hash as hash
import jwt

JWT_SECRET = "sdfsdfergfsfrmogperogmergpeorgm"
oath2schema = security.OAuth2PasswordBearer("/api/v1/login")


def create_db():
    return _db.Base.metadata.create_all(bind=_db.engine)


def get_db():
    database = _db.SessionLocal()
    try:
        yield database
    finally:
        database.close()


async def getUserByEmail(email: str, db: orm.Session):
    return db.query(UserModel).filter(UserModel.email == email).first()


async def create_user(user: schemas.UserRequest, db: orm.Session):
    # check for valid email address
    try:
        isValid = email_validator.validate_email(email=user.email)
    except:
        raise fastapi.HTTPException(
            status_code=400, detail='Invalid email address')

    # convert normal password to hash form
    hashed_password = hash.bcrypt.hash(user.password)

    # create the user model to be saved in database
    user_obj = UserModel(
        email=user.email,
        name=user.name,
        phone=user.phone,
        password_hash=hashed_password
    )

    # save the user in the db
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def create_token(user: UserModel):
    # convert user model to user schema
    user_schema = schemas.UserResponse.from_orm(user)
    # convert obj to dictionary
    user_dict = user_schema.dict()
    del user_dict["created_at"]

    token = jwt.encode(user_dict, JWT_SECRET)

    return dict(access_token=token, token_type="bearer")


async def login(email: str, password: str, db: orm.Session):
    db_user = await getUserByEmail(email=email, db=db)
    if not db_user:
        return False

    if not db_user.password_verification(password=password):
        return False

    return db_user


async def current_user(db: orm.Session = fastapi.Depends(get_db), token: str = fastapi.Depends(oath2schema)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        # get user by id and id is already available in the decoded user payload along with email phone and name
        db_user = db.query(UserModel).get(payload["id"])
    except:
        raise fastapi.HTTPException(status_code=401, detail="wrong Credentials")

    # if all ok then return the DTO/Schema version of User
    return schemas.UserResponse.from_orm(db_user)

async def create_post(user: schemas.UserResponse, db: orm.Session,
                      post: schemas.PostRequest):
    post = PostModel(**post.dict(), user_id=user.id)
    db.add(post)
    db.commit()
    db.refresh(post)
    # convert the post model to post DTO/Schema and return to API layer
    return schemas.PostResponse.from_orm(post)

async def get_posts_by_user(user: schemas.UserResponse, db: orm.Session):
    posts = db.query(PostModel).filter_by(user_id=user.id)
    # convert each post model to post schema and make a list to be returned
    return list(map(schemas.PostResponse.from_orm, posts))


async def get_posts_all(db: orm.Session):
    posts = db.query(PostModel)
    # convert each post model to post schema and make a list to be returned
    return list(map(schemas.PostResponse.from_orm, posts))


async def get_post_by_id(post_id: int, db: orm.Session):
    db_post = db.query(PostModel).filter(PostModel.id==post_id).first()
    if db_post is None:
        raise fastapi.HTTPException(
            status_code=401, detail="Wrong Login Credentials")
    return db_post

async def delete_post(post: PostModel, db: orm.Session):
    db.delete(post)
    db.commit()
    
    
async def update_post(post_request: schemas.PostRequest, post: PostModel, db: orm.Session):
    post.post_title = post_request.post_title
    post.post_description = post_request.post_description
    post.image = post_request.image
    
    db.commit()
    db.refresh(post)
    
    return schemas.PostResponse.from_orm(post)
    