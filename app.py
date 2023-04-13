import fastapi
import fastapi.security as security
import sqlalchemy.orm as orm
import schemas
import services
import uvicorn

app = fastapi.FastAPI()


@app.post("/api/v1/users")
async def register_user(
    user: schemas.UserRequest, db: orm.session = fastapi.Depends(services.get_db)
):
    # call to check if user with email exist
    db_user = await services.getUserByEmail(user.email, db)
    # if user found throw exception
    if db_user:
        raise fastapi.HTTPException(
            status_code=400, detail="Email already exist, try another email !")

    # create the user and return a token
    db_user = await services.create_user(user=user, db=db)
    return await services.create_token(db_user)


@app.post("/api/v1/login")
async def login(
    form_data: security.OAuth2PasswordRequestForm = fastapi.Depends(),
    db: orm.Session = fastapi.Depends(services.get_db)
):
    db_user = await services.login(email=form_data.username, password=form_data.password, db=db)

    if not db_user:
        raise fastapi.HTTPException(
            status_code=401, detail="Wrong Login Credentials")

    return await services.create_token(db_user)

@app.get("/api/users/current-user")
async def current_user(user: schemas.UserResponse = fastapi.Depends(services.current_user)):
    return user

@app.post("/api/v1/posts")
async def create_post(post: schemas.PostRequest,
                      user: schemas.UserRequest = fastapi.Depends(services.current_user),
                      db: orm.Session = fastapi.Depends(services.get_db)):
    return await services.create_post(user=user, post=post, db=db)
    
@app.get("/api/v1/posts/user")
async def get_post_by_user(user: schemas.UserRequest = fastapi.Depends(services.current_user),
                           db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts_by_user(user=user, db=db)

@app.get("/api/v1/posts/all")
async def get_post_all(db: orm.Session = fastapi.Depends(services.get_db)
):
    return await services.get_posts_all(db=db)

@app.get("/api/v1/post/{post_id}/", response_model=schemas.PostResponse)
async def get_post_by_id(post_id:int, db: orm.Session = fastapi.Depends(services.get_db)):
    post = await services.get_post_by_id(post_id=post_id, db=db)
    return post

@app.delete("/api/v1/posts/{post_id}/")
async def delete_post(post_id:int, db: orm.Session = fastapi.Depends(services.get_db),
                      user: schemas.UserRequest = fastapi.Depends(services.current_user)):
    post = await services.get_post_by_id(post_id=post_id, db=db)
    if post is None:
        raise fastapi.HTTPException(status_code=404, detail="Post not found")
    await services.delete_post(post=post, db=db)
    
    return "Post deleted successfully"


@app.put("/api/v1/posts/{post_id}", response_model=schemas.PostResponse)
async def update_post(post_id: int, new_post: schemas.PostRequest, db: orm.Session = fastapi.Depends(services.get_db)):
    db_post = await services.get_post_by_id(post_id=post_id, db=db)
    
    return await services.update_post(post_request=new_post, post=db_post, db=db)



if __name__ == "__main__":
    uvicorn.run("app:app", reload=True)
