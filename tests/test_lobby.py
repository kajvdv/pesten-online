import pytest




def test_create_lobby(client):
    count = 5
    for _ in range(count): # create lobbies
        response = client.post("/lobbies", json={'size': 2})
        assert response.status_code < 400, response.text
    response = client.get('/lobbies')
    assert response.status_code < 400, response.text
    print(response.json())
    assert len(response.json()) == count


if __name__ == "__main__":
    pytest.main([__file__])
