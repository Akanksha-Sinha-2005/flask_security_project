import pytest
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),'..')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING']=True
    with app.test_client() as client:
        yield client

def test_login_page(client):
    response=client.get("/login")
    assert response.status_code==200

def test_register_page(client):
    response=client.get("/register")
    assert response.status_code==200

def test_dashboard_redirect(client):
    response=client.get("/dashboard")
    assert response.status_code in [200,302
                                    
                                    ]