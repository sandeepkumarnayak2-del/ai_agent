from sqlalchemy import create_engine,Text,engine,Column,Integer,DateTime,String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# SQLite database file
DATABASE_URL = "sqlite:///./maxai.db"

engine=create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread":False}
)

SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base=declarative_base()

# ---- TABLES ----
class Conversation(Base):
    __tablename__ = "conversations"

    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String, index=True)
    role      = Column(String)
    content   = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)

class WordBank(Base):
    __tablename__ = "word_bank"

    id        = Column(Integer, primary_key=True, index=True)
    username  = Column(String, index=True)
    word      = Column(String)
    timestamp = Column(DateTime, default=datetime.now)

#create-table
def init_db():
    Base.metadata.create_all(bind=engine)
    print("db table created!")

def get_db():
    db=SessionLocal()

    try:
        yield db
    finally:
        db.close


def save_message(username:str, role:str,content:str):
    db=SessionLocal()
    msg=Conversation(
        username=username,
        role=role,
        content=content
    ) 
    db.add(msg)
    db.commit()
    db.close

def save_word(username:str,word:str):
    db = SessionLocal()
    existing=db.query(WordBank).filter(WordBank.username==username).filter(WordBank.word==word).first()

    if not existing:
        w = WordBank(username=username, word=word)
        db.add(w)
        db.commit()
    db.close()

def get_words(username: str):
    db = SessionLocal()
    words = db.query(WordBank)\
        .filter(WordBank.username == username)\
        .all()
    db.close()
    return [w.word for w in words]    

def get_history(username: str, limit: int = 20):
    db = SessionLocal()
    messages = db.query(Conversation)\
        .filter(Conversation.username == username)\
        .order_by(Conversation.timestamp.desc())\
        .limit(limit)\
        .all()
    db.close()
    return list(reversed(messages))

if __name__=="__main__":
    init_db()

    save_message("Sandeep", "user", "Hallo Max!")
    save_message("Sandeep", "assistant", "Hallo Sandeep! Wie geht es dir?")
    save_message("Sandeep", "user", "Teach me a word")

    history = get_history("Sandeep")

    print(f"\n chat history({len(history)} messages):")
    for msg in history:
        print(f"  {msg.role}: {msg.content}")

    # Test word bank
    save_word("Sandeep", "Hallo")
    save_word("Sandeep", "Danke")
    save_word("Sandeep", "Bitte")

    words = get_words("Sandeep")
    print(f"\n📖 Word bank: {words}")    

                  
def get_or_create_user(username: str):
    db=SessionLocal()

    from sqlalchemy import text
    result=db.execute(text("SELECT * FROM conversations WHERE username = :username LIMIT 1"),{"username": username}).fetchone()

    db.close()
    return username   