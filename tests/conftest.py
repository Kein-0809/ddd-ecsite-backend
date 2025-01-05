# Flaskアプリケーションのテストを簡単に行うための基本的なセットアップ

import pytest
from flask import Flask
from app import create_app, db


# テスト用アプリケーションを作成するフィクスチャ
@pytest.fixture
def app():
    """テスト用アプリケーション"""
    # テスト用のFlaskアプリケーションの設定を定義
    app = create_app({
        'TESTING': True,  # テストモードを有効にする
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # メモリ内SQLiteデータベースを使用
        'SECRET_KEY': 'test-secret-key',  # テスト用の秘密鍵
        'WTF_CSRF_ENABLED': False  # CSRF保護を無効にする
    })
    
    # テスト用のFlaskアプリケーションのDBのコンテキストを作成
    with app.app_context():
        db.create_all()  # テスト用のテーブルを作成
        yield app  # テストで使用するアプリケーションを返す
        db.drop_all()  # テスト後にテーブルを削除

# テストクライアントを作成するフィクスチャ
@pytest.fixture
def client(app):
    """テストクライアント"""
    return app.test_client()  # アプリケーションのテストクライアントを返す

# テスト用DBセッションを作成するフィクスチャ
@pytest.fixture
def db_session(app):
    """テスト用DBセッション"""
    with app.app_context():
        yield db.session  # テスト用のデータベースセッションを返す