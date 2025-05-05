import vcr

my_vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)


# Testing:
#
# from tests.vcr_config import my_vcr
#
# @my_vcr.use_cassette('some_api_call.yaml')
# def test_external_api(client):
#     response = client.get("/external-api")
#     assert response.status_code == 200
