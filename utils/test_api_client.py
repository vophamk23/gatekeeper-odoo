# -*- coding: utf-8 -*-
# Muc dich: Script Client doc lap chay tren may Windows de kiem thu tich hop (Integration Test) toan bo luong API.
#           Script nay:
#           1. Su dung odoo shell qua docker de tu dong cap/sinh Access Token (Bearer Token) bang subprocess pipe.
#           2. Su dung XML-RPC cua Odoo de thiet lap du lieu Demo (Chi nhanh, Khu vuc, Controller, Thiet bi, Nhan vien).
#           3. Gui HTTP POST (chua Bearer Token trong header) de test cac API:
#              - Heartbeat (/api/ControllerHeartbeat)
#              - Dong bo nhan su (/api/ControllerEmployeeSync)
#              - Day log quet the (/api/ControllerAccessLogUpload)
#           4. Kiem tra trang thai thuc te cua thiet bi va nhan vien trong Database Odoo.
#
# Cach chay: Mo Terminal o Windows va go:
#           python utils/test_api_client.py

import xmlrpc.client
import urllib.request
import json
import time
import subprocess
import os

# --- Cau hinh ket noi Odoo ---
ODOO_URL = "http://localhost:8070"
DB_NAME = "gatekeeper_db"
USER_NAME = "admin"
PASSWORD = "admin"  # Mat khau admin mac dinh trong file cau hinh docker
CONTAINER_NAME = "tnnt_odoo"

print("=== BAT DAU KIEM THU TICH HOP HE THONG GATE KEEPER ===")

# --- 1. Sinh / Lay Access Token (Bearer Token) tu dong qua Odoo Shell ---
print("\n1. Dang sinh API Access Token tu Odoo Shell...")
token = None
try:
    # Duong dan toi file generate_token.py
    script_path = os.path.join("utils", "generate_token.py")
    if not os.path.exists(script_path):
        print(f"[-] LOI: Khong tim thay file {script_path}")
        exit(1)
        
    with open(script_path, "r", encoding="utf-8") as f:
        script_content = f.read()
        
    # Chay docker exec odoo shell bang subprocess Popen va truyen stdin trực tiếp qua Python
    proc = subprocess.Popen(
        ["docker", "exec", "-i", CONTAINER_NAME, "odoo", "shell", "-d", DB_NAME],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL
    )
    stdout, _ = proc.communicate(input=script_content.encode("utf-8"))
    output = stdout.decode("utf-8")
    
    # Trich xuat TOKEN tu stdout
    for line in output.split('\n'):
        if line.strip().startswith('TOKEN:'):
            token = line.split('TOKEN:')[1].strip()
            break
            
    if not token:
        print("[-] LOI: Khong the tim thay chuoi TOKEN trong ket qua Odoo Shell.")
        print(f"Output nhan duoc: {output}")
        exit(1)
    print(f"[+] Sinh Token thanh cong! Token: {token[:10]}...{token[-10:]}")
except Exception as e:
    print(f"[-] LOI khi chay Odoo Shell: {e}")
    exit(1)

# --- 2. Ket noi Odoo qua XML-RPC de tu dong tao du lieu Demo ---
try:
    print("\n2. Dang ket noi Odoo XML-RPC de nap du lieu test...")
    common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
    uid = common.authenticate(DB_NAME, USER_NAME, PASSWORD, {})
    if not uid:
        print("[-] LOI: Khong the xac thuc tai khoan XML-RPC.")
        exit(1)
    
    models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")
except Exception as e:
    print(f"[-] LOI ket noi XML-RPC: {e}")
    exit(1)

# A. Kiem tra hoac tao Chi nhanh (Branch)
branch_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.branch', 'search', [[('name', '=', 'Chi nhanh Demo API')]])
if not branch_ids:
    branch_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.branch', 'create', [{
        'name': 'Chi nhanh Demo API',
        'timezone': 'Asia/Ho_Chi_Minh'
    }])
    print(f"[+] Da tao Chi nhanh moi ID: {branch_id}")
else:
    branch_id = branch_ids[0]
    print(f"[+] Su dung Chi nhanh san co ID: {branch_id}")

# B. Kiem tra hoac tao Khu vuc (Area)
area_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.area', 'search', [[('name', '=', 'Phong May Chu Demo')]])
if not area_ids:
    area_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.area', 'create', [{
        'name': 'Phong May Chu Demo',
        'branch_id': branch_id
    }])
    print(f"[+] Da tao Khu vuc moi ID: {area_id}")
else:
    area_id = area_ids[0]
    print(f"[+] Su dung Khu vuc san co ID: {area_id}")

# C. Kiem tra hoac tao Bo dieu khien (Controller)
ctrl_serial = "CTRL-API-DEMO-999"
ctrl_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.controller', 'search', [[('serial_number', '=', ctrl_serial)]])
if not ctrl_ids:
    ctrl_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.controller', 'create', [{
        'name': 'Bo dieu khien Demo',
        'serial_number': ctrl_serial,
        'branch_id': branch_id,
        'status': 'offline'
    }])
    print(f"[+] Da tao Bo dieu khien moi ID: {ctrl_id}")
else:
    ctrl_id = ctrl_ids[0]
    models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.controller', 'write', [[ctrl_id], {'status': 'offline'}])
    print(f"[+] Su dung Bo dieu khien san co ID: {ctrl_id} (Da reset offline)")

# D. Kiem tra hoac tao Thiet bi (Device)
dev_serial = "DEV-API-DEMO-999"
dev_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.device', 'search', [[('serial_number', '=', dev_serial)]])
if not dev_ids:
    dev_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.device', 'create', [{
        'name': 'Dau doc the Phong May Chu',
        'controller_id': ctrl_id,
        'area_id': area_id,
        'serial_number': dev_serial,
        'status': 'offline'
    }])
    print(f"[+] Da tao Thiet bi moi ID: {dev_id}")
else:
    dev_id = dev_ids[0]
    models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.device', 'write', [[dev_id], {'status': 'offline'}])
    print(f"[+] Su dung Thiet bi san co ID: {dev_id} (Da reset offline)")

# E. Kiem tra hoac tao Nhan vien (Employee)
emp_id = "EMP-API-DEMO-999"
emp_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.employee', 'search', [[('emp_id', '=', emp_id)]])
if not emp_ids:
    employee_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.employee', 'create', [{
        'name': 'Nguyen Van API Demo',
        'emp_id': emp_id,
        'branch_id': branch_id,
        'presence_state': 'outside'
    }])
    print(f"[+] Da tao Nhan vien moi ID: {employee_id}")
else:
    employee_id = emp_ids[0]
    models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.employee', 'write', [[employee_id], {'presence_state': 'outside', 'current_area_id': False}])
    print(f"[+] Su dung Nhan vien san co ID: {employee_id} (Da dat presence=outside)")

# F. Kiem tra hoac tao the RFID gan cho Nhan vien
card_code = "CARD-API-DEMO-999"
auth_ids = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.auth_info', 'search', [[('card_code', '=', card_code)]])
if not auth_ids:
    auth_id = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.auth_info', 'create', [{
        'employee_id': employee_id,
        'card_code': card_code,
        'active': True
    }])
    print(f"[+] Da dang ky The RFID Demo moi ID: {auth_id}")
else:
    print(f"[+] The RFID Demo da duoc dang ky tu truoc.")

print("[+] Thiet lap du lieu Demo hoan tat!")

# Helper de gui HTTP POST request kem Bearer Token trong header
def send_post_request(path, data):
    url = f"{ODOO_URL}{path}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    req_body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=req_body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as response:
            res_body = response.read().decode("utf-8")
            return json.loads(res_body)
    except urllib.error.HTTPError as e:
        print(f"[-] HTTP Error {e.code}: {e.read().decode('utf-8')}")
        return None
    except Exception as e:
        print(f"[-] Loi ket noi HTTP: {e}")
        return None

# --- 3. KIEM THU API 1: HEARTBEAT (/api/ControllerHeartbeat) ---
print("\n3. Dang kiem thu API Heartbeat...")
heartbeat_payload = {
    "serial_number": ctrl_serial
}
res_hb = send_post_request("/api/ControllerHeartbeat", heartbeat_payload)
print(f"[+] Ket qua API Heartbeat: {res_hb}")

# Kiem tra trang thai Controller trong DB da cap nhat online chua
time.sleep(1)
ctrl_data = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.controller', 'read', [[ctrl_id], ['status']])
print(f"[+] Kiem tra DB - Trang thai Bo dieu khien: {ctrl_data[0]['status']}")
assert ctrl_data[0]['status'] == 'online', "Loi: Trang thai Controller chua chuyen sang online!"

# --- 4. KIEM THU API 2: DONG BO NHAN SU (/api/ControllerEmployeeSync) ---
print("\n4. Dang kiem thu API Dong bo Nhan su...")
sync_payload = {
    "serial_number": ctrl_serial
}
res_sync = send_post_request("/api/ControllerEmployeeSync", sync_payload)
print(f"[+] Ket qua API Dong bo (Message): {res_sync.get('message')}")
print(f"[+] So luong nhan vien can dong bo tra ve: {len(res_sync.get('data', []))}")

# --- 5. KIEM THU API 3: QUET THE RA VAO (/api/ControllerAccessLogUpload) ---
print("\n5. Dang kiem thu API Quet the vao...")
upload_payload = {
    "serial_number": ctrl_serial,
    "device_serial": dev_serial,
    "card_value": card_code,
    "direction": "in",
    "verification_type": "card"
}
res_upload = send_post_request("/api/ControllerAccessLogUpload", upload_payload)
print(f"[+] Ket qua API Quet the: {res_upload}")

# Kiem tra xem log da duoc tao trong Odoo va nhan vien da doi presence_state thanh inside chua
time.sleep(1)
emp_data = models.execute_kw(DB_NAME, uid, PASSWORD, 't4.gate_keeper.employee', 'read', [[employee_id], ['presence_state', 'current_area_id']])
print(f"[+] Kiem tra DB - Trang thai hien dien cua nhan vien: {emp_data[0]['presence_state']}")
print(f"[+] Kiem tra DB - Vi tri khu vuc cua nhan vien: {emp_data[0]['current_area_id']}")
assert emp_data[0]['presence_state'] == 'inside', "Loi: Trang thai nhan vien chua chuyen thanh inside!"
assert emp_data[0]['current_area_id'] is not False, "Loi: Nhan vien chua cap nhat khu vuc hien tai!"

print("\n=== TAT CA KIEM THU API TICH HOP DEU THANH CONG (PASS) ===")
print("[+] Ban co the vao trinh duyet tai http://localhost:8070 de kiem tra cac ban ghi Access Log va Canh bao vua tao!")
