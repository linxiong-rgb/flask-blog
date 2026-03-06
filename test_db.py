from app import create_app, db
from app.models.gallery import Album, Photo
from sqlalchemy import text

app = create_app()
with app.app_context():
    # 检查 Photo 表的列
    result = db.session.execute(text("PRAGMA table_info(gallery_photo)"))
    columns = [row[1] for row in result]
    print("gallery_photo columns:", columns)
    
    # 检查用户
    from app.models.user import User
    users = User.query.all()
    print(f"Users: {len(users)}")
    
    # 检查相册
    albums = Album.query.all()
    print(f"Albums: {len(albums)}")
    
    # 检查照片
    try:
        photos = Photo.query.all()
        print(f"Photos: {len(photos)}")
    except Exception as e:
        print(f"Photos error: {e}")
