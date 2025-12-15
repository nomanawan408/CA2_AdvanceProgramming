import os

from models import Event


def test_root_public_homepage(client):
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code == 200


def test_root_redirect_superadmin(login_admin):
    resp = login_admin.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers["Location"].endswith("/admin/dashboard")


def test_root_redirect_organizer(login_organizer):
    resp = login_organizer.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers["Location"].endswith("/organizer/dashboard")


def test_root_redirect_student(login_student):
    resp = login_student.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302)
    assert resp.headers["Location"].endswith("/student/dashboard")


def test_invoice_route_serves_file(app, client, tmp_path):
    # Create a dummy invoice in the isolated static folder
    invoices_dir = os.path.join(app.static_folder, "invoices")
    filename = "test_invoice.png"
    file_path = os.path.join(invoices_dir, filename)
    with open(file_path, "wb") as f:
        f.write(b"invoice-bytes")

    resp = client.get(f"/invoices/{filename}")
    assert resp.status_code == 200
    assert resp.data == b"invoice-bytes"


def test_invoice_route_404_for_missing(client):
    resp = client.get("/invoices/does_not_exist.png")
    assert resp.status_code == 404
