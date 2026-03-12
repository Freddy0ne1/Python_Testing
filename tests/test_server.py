import pytest
from server import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_connexion_avec_email_inexistant_retourne_404(client):
    """Quand un email inexistant est saisi, l'application doit retourner 404 sans planter"""
    response = client.post('/showSummary', data={'email': 'inconnu@test.com'})
    assert response.status_code == 404

def test_connexion_avec_email_valide_retourne_page_bienvenue(client):
    """Quand un email valide est saisi, l'application doit afficher la page de bienvenue"""
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200