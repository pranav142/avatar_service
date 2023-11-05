import requests
import os
from dotenv import load_dotenv

load_dotenv()


headers = {
    'X-APP-ID': os.getenv("X_APP_ID"),
    'X-API-KEY': os.getenv("X_API_KEY")
}

url = "https://api.readyplayer.me/v1"

def get_all_assets(url):
    url = f'{url}/assets'
    response = requests.get(url, headers=headers)
    print(response.json())
    if response.status_code == 200:
        data = response.json()
        assets_data = data['data']
        assets = [(asset['id'], asset['name']) for asset in assets_data]

        for asset_id, asset_name in assets:
            print(f"ID: {asset_id}, Name: {asset_name}")
        return assets
    else:
        print(f"Failed to fetch data: {response.status_code} - {response.text}")
        return None

def equip_asset(url, avatar_id, asset_id):
    url = f'{url}/avatars/{avatar_id}/equip'
    
    headers = {
        'X-APP-ID': os.getenv("X_APP_ID"),
        'X-API-KEY': os.getenv("X_API_KEY"),
        'Content-Type': 'application/json' 
    }
    
    body = {
        "data": {
            "assetId": asset_id
        }
    }
    
    response = requests.put(url, headers=headers, json=body)
    
    if response.status_code == 204:
        print(f"Asset {asset_id} successfully equipped to avatar {avatar_id}.")
        return {"success": True}
    else:
        print(f"Failed to equip asset: {response.status_code} - {response.text}")
        return {"success": False}


def unequip_asset(url, avatar_id, asset_id):
    url = f'{url}/avatars/{avatar_id}/unequip'
    
    headers = {
        'X-APP-ID': os.getenv("X_APP_ID"),
        'X-API-KEY': os.getenv("X_API_KEY"),
        'Content-Type': 'application/json' 
    }
    
    body = {
        "data": {
            "assetId": asset_id
        }
    }
    
    response = requests.put(url, headers=headers, json=body)
    
    if response.status_code == 204:
        print(f"Asset {asset_id} successfully equipped to avatar {avatar_id}.")
        return {"success": True}
    else:
        print(f"Failed to equip asset: {response.status_code} - {response.text}")
        return {"success": False}

if __name__ == "__main__":
    # avatar_id = '6546e489e42e04abf89677cd'
    # asset_id = '148440358'
    
    # result = equip_asset(url, avatar_id, asset_id)
    assets = get_all_assets(url)
