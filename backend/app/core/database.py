"""
데이터베이스 연결 및 초기화 모듈
PostgreSQL과 InfluxDB 연결을 관리합니다.
"""

import os
import asyncio
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from dotenv import load_dotenv

load_dotenv()

# PostgreSQL 설정
POSTGRES_URL = os.getenv("POSTGRES_URL", "postgresql://user:password@localhost/odin_db")
engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# InfluxDB 설정
INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "your-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "your-org")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "odin_ohlcv")

# InfluxDB 클라이언트
influx_client = InfluxDBClient(
    url=INFLUX_URL,
    token=INFLUX_TOKEN,
    org=INFLUX_ORG
)

write_api = influx_client.write_api(write_options=SYNCHRONOUS)
query_api = influx_client.query_api()

def get_db():
    """데이터베이스 세션 생성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def init_db():
    """데이터베이스 초기화"""
    try:
        # PostgreSQL 테이블 생성
        Base.metadata.create_all(bind=engine)
        print("✅ PostgreSQL 데이터베이스 초기화 완료")
        
        # InfluxDB 버킷 확인 및 생성
        buckets_api = influx_client.buckets_api()
        try:
            buckets_api.find_bucket_by_name(INFLUX_BUCKET)
            print(f"✅ InfluxDB 버킷 '{INFLUX_BUCKET}' 확인됨")
        except:
            buckets_api.create_bucket(bucket_name=INFLUX_BUCKET, org=INFLUX_ORG)
            print(f"✅ InfluxDB 버킷 '{INFLUX_BUCKET}' 생성됨")
            
        print("✅ InfluxDB 연결 확인 완료")
        
    except Exception as e:
        print(f"⚠️ 데이터베이스 초기화 실패 (API는 정상 작동): {e}")
        print("💡 데이터베이스 없이도 백테스팅 API를 사용할 수 있습니다.")
        # 데이터베이스 오류를 무시하고 계속 진행
        pass

def close_db():
    """데이터베이스 연결 종료"""
    influx_client.close() 