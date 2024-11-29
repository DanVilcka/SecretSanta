from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

try:
    engine = create_engine('postgresql://postgres:postgres@localhost:5432/postgres')
    Session = sessionmaker(bind=engine)
    session = Session()

    print("Подключение к PostgreSQL установлено успешно")

except Exception as error:
    print("Ошибка при подключении к PostgreSQL", error)

finally:
    if session:
        session.close()
        print("Соединение с PostgreSQL закрыто")
