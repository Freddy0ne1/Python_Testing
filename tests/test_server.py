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

def test_points_du_club_sont_deduits_apres_reservation(client):
    """Les points du club doivent diminuer du nombre de places réservées"""
    from server import clubs
    club = [c for c in clubs if c['name'] == 'Simply Lift'][0]
    points_avant = int(club['points'])
    client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '2'
    })
    points_apres = int(club['points'])
    assert points_apres == points_avant - 2

def test_reservation_impossible_pour_competition_passee(client):
    """Le bouton Book Places ne doit pas apparaître pour une compétition passée"""
    response = client.post('/showSummary', data={'email': 'john@simplylift.co'})
    assert response.status_code == 200
    assert b'Book Places' not in response.data


def test_reservation_plus_de_12_places_est_bloquee(client):
    """La réservation doit être bloquée si le club demande plus de 12 places"""
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': '15'
    })
    assert response.status_code == 200
    assert b'Vous ne pouvez pas' in response.data


def test_reservation_bloquee_si_points_insuffisants(client):
    """La réservation doit être bloquée si le club n'a pas assez de points"""
    from server import clubs
    club = [c for c in clubs if c['name'] == 'Simply Lift'][0]
    points_disponibles = int(club['points'])
    response = client.post('/purchasePlaces', data={
        'competition': 'Spring Festival',
        'club': 'Simply Lift',
        'places': str(points_disponibles + 1)
    })
    assert response.status_code == 200
    assert b'Vous n&#39;avez pas assez de points' in response.data

def test_tableau_points_accessible_sans_connexion(client):
    """Le tableau des points doit être accessible sans connexion et afficher les clubs"""
    response = client.get('/pointsboard')
    assert response.status_code == 200
    assert b'Simply Lift' in response.data

def test_acces_page_reservation_club_valide(client):
    """La page de réservation doit s'afficher pour un club et une compétition valides"""
    response = client.get('/book/Spring Festival/Simply Lift')
    assert response.status_code == 200