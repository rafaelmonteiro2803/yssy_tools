import os
import requests
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TENANT_ID     = os.getenv("TENANT_ID", "4819c0ac-2467-422d-a1fd-618e47b30a45")
CLIENT_ID     = os.getenv("CLIENT_ID", "63d43218-3c42-4c04-8771-7259ae9cd58a")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "")
DYNAMICS_URL  = os.getenv("DYNAMICS_URL", "https://yssycrm.crm2.dynamics.com")
API_VERSION   = os.getenv("API_VERSION", "v9.2")
D365_USER     = os.getenv("D365_USER", "")      # seu email YSSY
D365_PASSWORD = os.getenv("D365_PASSWORD", "")  # sua senha


def get_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"

    # Tenta ROPC (usuário + senha) se credenciais disponíveis
    if D365_USER and D365_PASSWORD:
        data = {
            "grant_type":    "password",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "username":      D365_USER,
            "password":      D365_PASSWORD,
            "scope":         f"{DYNAMICS_URL}/.default openid profile",
        }
    else:
        # Fallback: client credentials
        data = {
            "grant_type":    "client_credentials",
            "client_id":     CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "scope":         f"{DYNAMICS_URL}/.default",
        }

    r = requests.post(url, data=data, timeout=15)
    r.raise_for_status()
    return r.json()["access_token"]


def dynamics_get(endpoint, params=None):
    token = get_token()
    base  = f"{DYNAMICS_URL}/api/data/{API_VERSION}/{endpoint}"
    headers = {
        "Authorization":    f"Bearer {token}",
        "Accept":           "application/json",
        "OData-MaxVersion": "4.0",
        "OData-Version":    "4.0",
        "Prefer":           "odata.include-annotations=*",
    }
    r = requests.get(base, headers=headers, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/opportunities")
def opportunities():
    try:
        select = (
            "name,estimatedvalue,stepname,closeprobability,"
            "actualclosedate,estimatedclosedate,"
            "_ownerid_value,_customerid_value,createdon,statuscode"
        )
        data = dynamics_get("opportunities", {
            "$select":  select,
            "$top":     500,
            "$orderby": "createdon desc",
        })
        return jsonify({"ok": True, "data": data.get("value", [])})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/accounts")
def accounts():
    try:
        select = "name,address1_city,address1_stateorprovince,industrycode,revenue,numberofemployees,createdon"
        data = dynamics_get("accounts", {
            "$select":  select,
            "$top":     300,
            "$orderby": "createdon desc",
        })
        return jsonify({"ok": True, "data": data.get("value", [])})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/contacts")
def contacts():
    try:
        select = "fullname,emailaddress1,jobtitle,telephone1,_parentcustomerid_value,createdon"
        data = dynamics_get("contacts", {
            "$select":  select,
            "$top":     300,
            "$orderby": "createdon desc",
        })
        return jsonify({"ok": True, "data": data.get("value", [])})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/metrics")
def metrics():
    try:
        opps  = dynamics_get("opportunities", {
            "$select": "estimatedvalue,stepname,statuscode",
            "$top":    1000,
        })
        items  = opps.get("value", [])
        open_v = [o for o in items if o.get("statuscode") == 1]
        won_v  = [o for o in items if o.get("statuscode") == 2]
        pipeline  = sum(o.get("estimatedvalue") or 0 for o in open_v)
        won_total = sum(o.get("estimatedvalue") or 0 for o in won_v)
        avg       = (pipeline / len(open_v)) if open_v else 0
        total_cl  = len(won_v) + len([o for o in items if o.get("statuscode") == 3])
        win_rate  = (len(won_v) / total_cl * 100) if total_cl else 0
        return jsonify({
            "ok":       True,
            "total":    len(items),
            "open":     len(open_v),
            "pipeline": pipeline,
            "won_total":won_total,
            "avg_deal": avg,
            "win_rate": round(win_rate, 1),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/ping")
def ping():
    try:
        get_token()
        return jsonify({"ok": True, "msg": "Autenticação bem-sucedida."})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
