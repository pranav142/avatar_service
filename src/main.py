from flask import Flask, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from rpm_sdk import equip_asset
load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'database': os.getenv('DB_NAME')
}

url = "https://api.readyplayer.me/v1"

class Database:
    def __enter__(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()


def get_avatar_tier(cursor, user_id): 
    cursor.execute("SELECT avatar_tier FROM Users WHERE user_id = %s", (user_id,))
    avatar_tier = cursor.fetchone()
    return avatar_tier

def upgrade_tier(cursor, current_tier, max, user_id):
    new_tier = current_tier[0] if current_tier else None
    if current_tier and current_tier[0] < max: 
        new_tier = current_tier[0] + 1
        cursor.execute("UPDATE Users SET avatar_tier = %s WHERE user_id = %s", (new_tier, user_id))
    return new_tier

def downgrade_tier(cursor, current_tier, user_id, min=0):
    new_tier = current_tier[0] if current_tier else None
    if current_tier and current_tier[0] > min: 
        new_tier = current_tier[0] - 1
        cursor.execute("UPDATE Users SET avatar_tier = %s WHERE user_id = %s", (new_tier, user_id))
    return new_tier

def get_avatar_url(cursor, user_id):
    cursor.execute("SELECT avatar_url FROM Users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    return result

def extract_id_from_url(url):
    return url.rsplit('/', 1)[-1].split('.glb')[0]

def get_asset_id(cursor, avatar_tier):
    cursor.execute("SELECT asset_id FROM Avatars WHERE avatar_tier = %s", (avatar_tier,))
    avatar_id = cursor.fetchone()
    return avatar_id


def equip_new_asset(cursor, user_id, new_tier):
    avatar_url = get_avatar_url(cursor, user_id) 
    avatar_id = extract_id_from_url(avatar_url[0])

    asset_id = get_asset_id(cursor, new_tier)
    result = equip_asset(url, avatar_id, str(asset_id[0]))
    return result

@app.route('/avatars/<user_id>', methods=['GET'])
def get_avatar(user_id):
    with Database() as cursor:
        result = get_avatar_url(cursor, user_id)
    
    if result:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'User not found'}), 404

@app.route('/avatars/upgrade/<user_id>', methods=['PUT'])
def upgrade_avatar_tier(user_id):
    with Database() as cursor:
        old_tier = get_avatar_tier(cursor, user_id)
        new_tier = upgrade_tier(cursor, old_tier, 20, user_id)

        result = equip_new_asset(cursor, user_id, new_tier)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'couldnt upgrade avatar'}), 404

@app.route('/avatars/downgrade/<user_id>', methods=['PUT'])
def downgrade_avatar_tier(user_id):
    with Database() as cursor:
        old_tier = get_avatar_tier(cursor, user_id)
        new_tier = downgrade_tier(cursor, old_tier, user_id)
        
        result = equip_new_asset(cursor, user_id, new_tier)

    if result["success"]:
        return jsonify(result), 200
    else:
        return jsonify({'error': 'couldnt downgrade avatar'}), 404

if __name__ == '__main__':
    with Database() as cursor:
        print(extract_id_from_url(get_avatar_url(cursor, 3)[0]))
        asset_id = get_asset_id(cursor, 6)
        print(asset_id[0])
    app.run(debug=True)
