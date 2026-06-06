from fastapi.testclient import TestClient

from app.main import app


def get_category_id(client: TestClient, category_name: str) -> int:
    response = client.get("/categories")
    assert response.status_code == 200
    category = next(
        item for item in response.json() if item["name"] == category_name
    )
    return category["id"]


def test_lifespan_seeds_relational_expenses() -> None:
    with TestClient(app) as client:
        response = client.get("/expenses")

    assert response.status_code == 200
    expenses = response.json()
    wedding = next(expense for expense in expenses if expense["name"] == "Casamento")

    assert wedding["category"]["name"] == "Casamento"
    assert wedding["type"] == "installment"
    assert wedding["total_value"] == "60800.00"
    assert len(wedding["payments"]) == 24
    assert wedding["totals"]["paid_installments"] == 3
    assert wedding["totals"]["remaining_installments"] == 19


def test_create_expense_and_payment() -> None:
    with TestClient(app) as client:
        category_id = get_category_id(client, "Hardware")

        expense_response = client.post(
            "/expenses",
            json={
                "category_id": category_id,
                "name": "Monitor",
                "type": "one_time",
                "total_value": "1200.00",
            },
        )
        assert expense_response.status_code == 201
        expense_id = expense_response.json()["id"]
        assert expense_response.json()["category"]["name"] == "Hardware"

        payment_response = client.post(
            f"/expenses/{expense_id}/payments",
            json={
                "kind": "single",
                "status": "planned",
                "amount": "1200.00",
                "repeats": "none",
            },
        )

    assert payment_response.status_code == 201
    assert payment_response.json()["expense_id"] == expense_id


def test_create_recurrent_expense_with_monthly_payment() -> None:
    with TestClient(app) as client:
        category_id = get_category_id(client, "Academia")

        expense_response = client.post(
            "/expenses",
            json={
                "category_id": category_id,
                "name": "Pilates",
                "type": "recurrent",
                "total_value": None,
                "starts_on": "2026-06-05",
                "ends_on": None,
            },
        )
        assert expense_response.status_code == 201
        expense_id = expense_response.json()["id"]

        payment_response = client.post(
            f"/expenses/{expense_id}/payments",
            json={
                "kind": "recurring",
                "status": "planned",
                "amount": "250.00",
                "due_date": "2026-06-05",
                "repeats": "monthly",
                "repeat_day": 5,
            },
        )

        expense_detail_response = client.get(f"/expenses/{expense_id}")

    assert payment_response.status_code == 201
    assert payment_response.json()["kind"] == "recurring"
    assert payment_response.json()["due_date"] == "2026-06-05"
    assert payment_response.json()["repeat_day"] == 5
    assert expense_detail_response.status_code == 200
    assert expense_detail_response.json()["type"] == "recurrent"
    assert expense_detail_response.json()["total_value"] is None
    assert len(expense_detail_response.json()["payments"]) == 1


def test_rejects_payment_kind_that_does_not_match_expense_type() -> None:
    with TestClient(app) as client:
        category_id = get_category_id(client, "Academia")

        expense_response = client.post(
            "/expenses",
            json={
                "category_id": category_id,
                "name": "Gym",
                "type": "recurrent",
                "total_value": None,
            },
        )
        assert expense_response.status_code == 201
        expense_id = expense_response.json()["id"]

        invalid_payment_response = client.post(
            f"/expenses/{expense_id}/payments",
            json={
                "kind": "single",
                "status": "planned",
                "amount": "300.00",
                "repeats": "none",
            },
        )

    assert invalid_payment_response.status_code == 422
    assert invalid_payment_response.json()["detail"] == (
        "single payments are not allowed for recurrent expenses."
    )


def test_category_crud_renames_expenses_and_blocks_delete_when_used() -> None:
    with TestClient(app) as client:
        category_id = get_category_id(client, "Hardware")

        expense_response = client.post(
            "/expenses",
            json={
                "category_id": category_id,
                "name": "Monitor",
                "type": "one_time",
                "total_value": "1200.00",
            },
        )
        assert expense_response.status_code == 201

        duplicate_response = client.post("/categories", json={"name": "Hardware"})
        assert duplicate_response.status_code == 409

        update_response = client.put(
            f"/categories/{category_id}",
            json={"name": "Home office"},
        )
        assert update_response.status_code == 200
        assert update_response.json()["name"] == "Home office"

        expenses_response = client.get("/expenses")
        assert expenses_response.status_code == 200
        monitor = next(
            expense
            for expense in expenses_response.json()
            if expense["name"] == "Monitor"
        )
        assert monitor["category_id"] == category_id
        assert monitor["category"]["name"] == "Home office"

        delete_used_response = client.delete(f"/categories/{category_id}")
        assert delete_used_response.status_code == 409

        client.delete(f"/expenses/{expense_response.json()['id']}")
        delete_response = client.delete(f"/categories/{category_id}")
        assert delete_response.status_code == 204


def test_income_crud_lists_newest_first_and_trims_source() -> None:
    with TestClient(app) as client:
        first_response = client.post(
            "/incomes",
            json={
                "source": "  Freelance  ",
                "amount": "1200.00",
                "received_on": "2026-05-20",
                "notes": "Landing page",
            },
        )
        assert first_response.status_code == 201
        first_income_id = first_response.json()["id"]
        assert first_response.json()["source"] == "Freelance"

        second_response = client.post(
            "/incomes",
            json={
                "source": "Salary",
                "amount": "5000.00",
                "received_on": "2026-06-05",
                "notes": None,
            },
        )
        assert second_response.status_code == 201

        list_response = client.get("/incomes")
        assert list_response.status_code == 200
        assert [income["source"] for income in list_response.json()] == [
            "Salary",
            "Freelance",
        ]

        update_response = client.put(
            f"/incomes/{first_income_id}",
            json={
                "source": "Consulting",
                "amount": "1300.00",
                "received_on": "2026-05-21",
                "notes": "Updated",
            },
        )
        assert update_response.status_code == 200
        assert update_response.json()["source"] == "Consulting"
        assert update_response.json()["amount"] == "1300.00"

        delete_response = client.delete(f"/incomes/{first_income_id}")
        assert delete_response.status_code == 204

        missing_response = client.get(f"/incomes/{first_income_id}")
        assert missing_response.status_code == 404


def test_rejects_blank_income_source() -> None:
    with TestClient(app) as client:
        response = client.post(
            "/incomes",
            json={
                "source": "   ",
                "amount": "1200.00",
                "received_on": "2026-06-05",
            },
        )

    assert response.status_code == 422
    assert response.json()["detail"] == "Income source is required."


def test_update_and_delete_expense_and_payment() -> None:
    with TestClient(app) as client:
        category_id = get_category_id(client, "Academia")

        expense_response = client.post(
            "/expenses",
            json={
                "category_id": category_id,
                "name": "Gym",
                "type": "recurrent",
                "total_value": None,
            },
        )
        expense_id = expense_response.json()["id"]

        updated_expense_response = client.put(
            f"/expenses/{expense_id}",
            json={
                "category_id": category_id,
                "name": "Updated Gym",
                "type": "recurrent",
                "total_value": None,
            },
        )
        assert updated_expense_response.status_code == 200
        assert updated_expense_response.json()["name"] == "Updated Gym"

        payment_response = client.post(
            f"/expenses/{expense_id}/payments",
            json={
                "kind": "recurring",
                "status": "pending",
                "amount": "300.00",
                "repeats": "monthly",
            },
        )
        payment_id = payment_response.json()["id"]

        updated_payment_response = client.put(
            f"/payments/{payment_id}",
            json={
                "kind": "recurring",
                "status": "due",
                "amount": "300.00",
                "repeats": "monthly",
                "paid_at": "2026-06-05",
            },
        )
        assert updated_payment_response.status_code == 200
        assert updated_payment_response.json()["status"] == "due"

        delete_payment_response = client.delete(f"/payments/{payment_id}")
        assert delete_payment_response.status_code == 204

        delete_expense_response = client.delete(f"/expenses/{expense_id}")
        assert delete_expense_response.status_code == 204
