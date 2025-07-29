import requests

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYmhpamVldHN1cnlhd2Fuc2hpMTI4QGdtYWlsLmNvbSIsImV4cCI6MTc1NDM5MTA0Mn0.bdAs68I2gt6Gogz9Rv3giABdfUindimjS3tsQ7fSavE"
headers = {"Authorization": f"Bearer {token}"}
response = requests.get("http://127.0.0.1:5000/profile/me", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")