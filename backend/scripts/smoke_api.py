"""Smoke-test API for employee / manager / hr / admin."""
from __future__ import annotations

import json
import sys

import httpx

BASE = "http://127.0.0.1:8000/api/v1"
PASS = "Password123!"
USERS = {
    "employee": "employee@kedo.local",
    "manager": "manager@kedo.local",
    "hr": "hr@kedo.local",
    "admin": "admin@kedo.local",
}

failed: list[str] = []
ok_count = 0


def check(label: str, cond: bool, detail: str = "") -> None:
    global ok_count
    if cond:
        ok_count += 1
        print(f"  OK  {label}")
    else:
        failed.append(f"{label}: {detail}")
        print(f" FAIL {label}: {detail}")


def login(client: httpx.Client, email: str) -> str | None:
    r = client.post(f"{BASE}/auth/login", json={"email": email, "password": PASS})
    if r.status_code != 200:
        check(f"login {email}", False, f"{r.status_code} {r.text[:200]}")
        return None
    data = r.json()
    check(f"login {email}", "access_token" in data)
    return data["access_token"]


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def main() -> int:
    with httpx.Client(timeout=30.0) as client:
        health = client.get("http://127.0.0.1:8000/health")
        check("health", health.status_code == 200, health.text)

        tokens: dict[str, str] = {}
        for role, email in USERS.items():
            t = login(client, email)
            if t:
                tokens[role] = t

        if len(tokens) < 4:
            print("\nCannot continue without all role tokens")
            return 1

        # --- employee ---
        te = tokens["employee"]
        he = auth_headers(te)
        me = client.get(f"{BASE}/users/me", headers=he)
        check("employee /me", me.status_code == 200 and me.json().get("role") == "employee", me.text[:200])
        emp_id = me.json()["id"]

        dicts = client.get(f"{BASE}/dictionaries/statuses", headers=he)
        check("employee dictionaries", dicts.status_code == 200 and len(dicts.json()) >= 6, dicts.text[:200])
        statuses = {s["name"]: s["id"] for s in dicts.json()}
        types = {
            t["name"]: t["id"]
            for t in client.get(f"{BASE}/dictionaries/request-types", headers=he).json()
        }
        type_id = next(iter(types.values()))

        create = client.post(
            f"{BASE}/requests",
            headers=he,
            json={"request_type_id": type_id, "comment": "smoke test leave"},
        )
        check("employee create request", create.status_code == 201, create.text[:300])
        req = create.json() if create.status_code == 201 else None
        req_id = req["id"] if req else None

        my_reqs = client.get(f"{BASE}/requests", headers=he)
        check("employee list own requests", my_reqs.status_code == 200, my_reqs.text[:200])

        # employee cannot access stats
        stats_emp = client.get(f"{BASE}/requests/stats", headers=he)
        check("employee stats forbidden", stats_emp.status_code == 403, stats_emp.text[:200])

        # employee cannot read admin audit
        audit_emp = client.get(f"{BASE}/admin/audit", headers=he)
        check("employee audit forbidden", audit_emp.status_code == 403, audit_emp.text[:200])

        # --- hr ---
        th = tokens["hr"]
        hh = auth_headers(th)
        me_hr = client.get(f"{BASE}/users/me", headers=hh)
        check("hr /me role", me_hr.status_code == 200 and me_hr.json().get("role") == "hr", me_hr.text[:200])

        stats = client.get(f"{BASE}/requests/stats", headers=hh)
        check("hr stats", stats.status_code == 200 and "created" in stats.json(), stats.text[:300])

        all_reqs = client.get(f"{BASE}/requests", headers=hh)
        check("hr list all requests", all_reqs.status_code == 200, all_reqs.text[:200])

        if emp_id:
            by_emp = client.get(f"{BASE}/requests", headers=hh, params={"employee_id": emp_id})
            check("hr filter employee_id", by_emp.status_code == 200, by_emp.text[:200])

            card = client.get(f"{BASE}/users/{emp_id}", headers=hh)
            check("hr read employee profile", card.status_code == 200, card.text[:200])

            pd = client.get(f"{BASE}/users/{emp_id}/private-data", headers=hh)
            # may 404 if no private data row
            check(
                "hr private-data access",
                pd.status_code in (200, 404),
                pd.text[:200],
            )

        admin_users_hr = client.get(f"{BASE}/admin/users", headers=hh)
        check("hr admin users list", admin_users_hr.status_code == 200, admin_users_hr.text[:200])

        if req_id and "На проверке" in statuses:
            patch = client.patch(
                f"{BASE}/requests/{req_id}",
                headers=hh,
                json={"status_id": statuses["На проверке"]},
            )
            check("hr -> На проверке", patch.status_code == 200, patch.text[:300])
            if patch.status_code == 200 and "На согласовании" in statuses:
                patch2 = client.patch(
                    f"{BASE}/requests/{req_id}",
                    headers=hh,
                    json={"status_id": statuses["На согласовании"]},
                )
                check("hr -> На согласовании", patch2.status_code == 200, patch2.text[:300])

        # --- manager ---
        tm = tokens["manager"]
        hm = auth_headers(tm)
        me_m = client.get(f"{BASE}/users/me", headers=hm)
        check("manager /me role", me_m.status_code == 200 and me_m.json().get("role") == "manager", me_m.text[:200])

        dept_reqs = client.get(f"{BASE}/requests", headers=hm)
        check("manager list dept requests", dept_reqs.status_code == 200, dept_reqs.text[:200])

        if req_id and "Одобрена" in statuses:
            approve = client.patch(
                f"{BASE}/requests/{req_id}",
                headers=hm,
                json={"status_id": statuses["Одобрена"]},
            )
            check("manager approve", approve.status_code == 200, approve.text[:300])

        # --- admin ---
        ta = tokens["admin"]
        ha = auth_headers(ta)
        me_a = client.get(f"{BASE}/users/me", headers=ha)
        check("admin /me role", me_a.status_code == 200 and me_a.json().get("role") == "admin", me_a.text[:200])

        audit = client.get(f"{BASE}/admin/audit", headers=ha)
        check("admin audit", audit.status_code == 200, audit.text[:200])

        users = client.get(f"{BASE}/admin/users", headers=ha)
        check("admin users list", users.status_code == 200 and len(users.json()) > 0, users.text[:200])

        # notifications for employee after workflow
        notif = client.get(f"{BASE}/notifications", headers=he)
        check("employee notifications", notif.status_code == 200, notif.text[:200])

        # refresh token
        login_r = client.post(
            f"{BASE}/auth/login",
            json={"email": USERS["employee"], "password": PASS},
        )
        refresh = login_r.json().get("refresh_token")
        if refresh:
            ref = client.post(f"{BASE}/auth/refresh", json={"refresh_token": refresh})
            check("auth refresh", ref.status_code == 200, ref.text[:200])

        # logout
        lo = client.post(
            f"{BASE}/auth/logout",
            headers=he,
            json={"refresh_token": None, "all_sessions": True},
        )
        check("auth logout", lo.status_code == 200, lo.text[:200])

    print()
    print(f"Passed: {ok_count}, Failed: {len(failed)}")
    for f in failed:
        print(" -", f)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
