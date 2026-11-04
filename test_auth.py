import os, sys, tempfile
db = os.path.join(tempfile.mkdtemp(), "t.db")
os.environ["DATABASE_URL"] = f"sqlite:///{db}"; os.environ["SECRET_KEY"] = "testkey"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fastapi.testclient import TestClient
from main import app
from make_admin import set_role
c = TestClient(app)
art = {"title": "a", "description": "b", "author": "c"}

def check(name, got, want):
    print(("PASS " if got == want else "FAIL ") + f"{name}: {got}" + ("" if got == want else f" (wanted {want})"))
    assert got == want

def login(u, p):
    return {"Authorization": "Bearer " + c.post("/auth/token", data={"username": u, "password": p}).json()["access_token"]}

for u in ("alice", "owner"):
    r = c.post("/auth/register", json={"username": u, "email": f"{u}@x.com", "password": "S3cretPass!"})
    check(f"register {u}", r.status_code, 201)
    check(f"{u} starts as user", r.json()["role"], "user")
check("duplicate", c.post("/auth/register", json={"username": "alice", "email": "alice@x.com", "password": "S3cretPass!"}).status_code, 409)
check("wrong password", c.post("/auth/token", data={"username": "alice", "password": "nope"}).status_code, 401)
set_role("owner", "admin")
U, A = login("alice", "S3cretPass!"), login("owner", "S3cretPass!")

print("--- art catalog")
check("public can read", c.get("/art").status_code, 200)
check("anonymous cannot create", c.post("/art", json=art).status_code, 401)
check("normal user cannot create", c.post("/art", json=art, headers=U).status_code, 403)
check("admin can create", c.post("/art", json=art, headers=A).status_code, 200)
aid = c.get("/art").json()["art"][0]["id"]
check("normal user cannot update", c.put(f"/art/{aid}", json=art, headers=U).status_code, 403)
check("normal user cannot delete", c.delete(f"/art/{aid}", headers=U).status_code, 403)
check("normal user cannot export", c.get("/art/export", headers=U).status_code, 403)
check("admin can update", c.put(f"/art/{aid}", json=art, headers=A).status_code, 200)
check("admin can delete", c.delete(f"/art/{aid}", headers=A).status_code, 200)

print("--- chat")
check("anonymous cannot read chat", c.get("/chat").status_code, 401)
check("anonymous cannot post", c.post("/chat", json={"content": "hi"}).status_code, 401)
m1 = c.post("/chat", json={"content": "  hello everyone  "}, headers=U); check("user posts", m1.status_code, 201)
check("content trimmed", m1.json()["content"], "hello everyone")
c.post("/chat", json={"content": "welcome!"}, headers=A)
check("blank rejected", c.post("/chat", json={"content": "   "}, headers=U).status_code, 422)
check("too long rejected", c.post("/chat", json={"content": "x" * 501}, headers=U).status_code, 422)
msgs = c.get("/chat", headers=U).json()
check("history oldest->newest", [m["username"] for m in msgs], ["alice", "owner"])
check("polling after_id", len(c.get(f"/chat?after_id={msgs[0]['id']}", headers=U).json()), 1)
check("user cannot delete message", c.delete(f"/chat/{msgs[0]['id']}", headers=U).status_code, 403)
check("admin can delete message", c.delete(f"/chat/{msgs[0]['id']}", headers=A).status_code, 200)
check("message gone", len(c.get("/chat", headers=U).json()), 1)

print("--- role cannot be forged")
r = c.post("/auth/register", json={"username": "evil", "email": "e@x.com", "password": "S3cretPass!", "role": "admin"})
check("register ignores role field", r.json()["role"], "user")
set_role("owner", "user")
check("demotion is immediate", c.post("/art", json=art, headers=A).status_code, 403)
print("ALL PASSED")
