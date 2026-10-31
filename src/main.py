from database import initialize, initialize_history
from request_service import (
    PRIORITIES,
    STATUSES,
    create_request,
    list_requests,
    get_request,
    update_request,
    close_request,
    get_request_history,
)


from quality import (
    review_records,
    valid_resolution,
    correct_resolution,
)


def show_request(record):
    if record is None:
        print("\nRequest not found.")
        return

    print("\n" + "-" * 45)
    print(f"Request: SR-{record['id']:04d}")
    print("-" * 45)
    print(f"Title:       {record['title']}")
    print(f"Category:    {record['category']}")
    print(f"Priority:    {record['priority']}")
    print(f"Status:      {record['status']}")
    print(f"Assigned to: {record['assigned_to']}")
    print(f"Created:     {record['created_at']}")
    print(f"Resolution:  {record['resolution'] or 'Not provided'}")
    print("-" * 45)


def read_id():
    value = input(
        "Request ID (2, SR0002, or SR-0002): "
    ).strip().upper()

    if value.startswith("SR-"):
        value = value[3:]
    elif value.startswith("SR"):
        value = value[2:]

    if not value.isdigit() or int(value) < 1:
        raise ValueError("Enter a valid request ID.")

    return int(value)


def show_history(request_id):
    record = get_request(request_id)

    if record is None:
        print("\nRequest not found.")
        return

    history = get_request_history(request_id)

    print("\n" + "=" * 50)
    print(f" REQUEST HISTORY — SR-{request_id:04d}")
    print("=" * 50)
    print(f"Issue: {record['title']}")

    if not history:
        print("\nNo history recorded for this request.")
        return

    for entry in history:
        print("\n" + "-" * 50)
        print(f"Date:    {entry['recorded_at']}")
        print(f"Action:  {entry['action']}")
        print(f"Details: {entry['details']}")

    print("-" * 50)


def create_new_request():
    print("\n--- CREATE SUPPORT REQUEST ---")

    title = input("Issue / Request: ").strip()
    category = input("Category: ").strip()

    print("\nAvailable priorities:")
    for index, priority in enumerate(PRIORITIES, start=1):
        print(f"[{index}] {priority}")

    selection = input("\nSelect priority (number or name): ").strip()

    if selection.isdigit():
        number = int(selection)

        if 1 <= number <= len(PRIORITIES):
            priority = PRIORITIES[number - 1]
        else:
            raise ValueError("Invalid priority selection.")
    else:
        priority = selection.title()

    request_id = create_request(title, category, priority)

    print(f"\nRequest SR-{request_id:04d} created successfully.")


def view_all_requests():
    records = list_requests()

    print("\n--- SUPPORT REQUESTS ---")

    if not records:
        print("No requests found.")
        return

    print("-" * 75)

    for record in records:
        print(
            f"SR-{record['id']:04d} | "
            f"{record['priority']:<8} | "
            f"{record['status']:<12} | "
            f"{record['title']}"
        )

    print("-" * 75)
    print(f"Total requests: {len(records)}")


def search_request():
    print("\n--- SEARCH REQUEST ---")

    request_id = read_id()
    record = get_request(request_id)

    show_request(record)


def assign_request():
    print("\n--- UPDATE / ASSIGN REQUEST ---")

    request_id = read_id()
    record = get_request(request_id)

    if record is None:
        print("\nRequest not found.")
        return

    show_request(record)

    print("\nAvailable statuses:")
    for index, status in enumerate(STATUSES, start=1):
        print(f"[{index}] {status}")

    selection = input("\nSelect status (number or name): ").strip()

    if selection.isdigit():
        number = int(selection)

        if 1 <= number <= len(STATUSES):
            status = STATUSES[number - 1]
        else:
            raise ValueError("Invalid status selection.")
    else:
        status = next(
            (
                item for item in STATUSES
                if item.lower() == selection.lower()
            ),
            None,
        )

        if status is None:
            raise ValueError("Invalid status.")

    assigned_to = input("Assigned to: ").strip()

    if update_request(request_id, status, assigned_to):
        print(f"\nSR-{request_id:04d} updated successfully.")
    else:
        print("\nRequest could not be updated.")


def close_existing_request():
    print("\n--- CLOSE SUPPORT REQUEST ---")

    request_id = read_id()
    record = get_request(request_id)

    if record is None:
        print("\nRequest not found.")
        return

    if record["status"] == "Closed":
        print("\nThis request is already closed.")
        return

    show_request(record)

    resolution = input("\nResolution notes: ").strip()

    if not resolution:
        raise ValueError("Resolution notes are required.")

    if not valid_resolution(resolution):
        raise ValueError(
            "Resolution needs at least 15 characters "
            "and 3 words."
        )

    confirm = input("Confirm closure? (y/n): ").strip().lower()

    if confirm != "y":
        print("\nClosure cancelled.")
        return

    if close_request(request_id, resolution):
        print(f"\nSR-{request_id:04d} closed successfully.")
    else:
        print("\nRequest could not be closed.")



def review_support_records():
    total, findings = review_records()

    print("\n--- RECORD VERIFICATION ---")
    print(f"Records reviewed: {total}")
    print(f"Records needing attention: {len(findings)}")

    if not findings:
        print("No validation issues found.")
        return

    for item in findings:
        print(f"\nSR-{item['id']:04d}: {item['title']}")
        for issue in item["issues"]:
            print(f"  - {issue}")


def correct_request_resolution():
    print("\n--- CORRECT RESOLUTION ---")
    request_id = read_id()
    record = get_request(request_id)

    if record is None:
        print("Request not found.")
        return

    show_request(record)
    resolution = input("Corrected resolution: ").strip()

    if not valid_resolution(resolution):
        raise ValueError(
            "Enter at least 15 characters and 3 words."
        )

    confirm = input("Save correction? (y/n): ").strip().lower()
    if confirm != "y":
        print("Correction cancelled.")
        return

    if correct_resolution(request_id, resolution):
        print("Resolution corrected successfully.")


from reporting import generate_report, export_report


def main():
    initialize()
    initialize_history()

    while True:
        print("\n" + "=" * 48)
        print(" TECHNICAL OPERATIONS SUPPORT SYSTEM")
        print("=" * 48)
        print("[1] Create Support Request")
        print("[2] View All Requests")
        print("[3] Search Request")
        print("[4] Update / Assign Request")
        print("[5] Close Request")
        print("[6] View Request History")
        print("[7] Review Records")
        print("[8] Correct Resolution")
        print("[9] View Operational Report")
        print("[10] Export Report")
        print("[0] Exit")
        print("-" * 48)

        choice = input("\nSelect option: ").strip()

        try:
            if choice == "1":
                create_new_request()

            elif choice == "2":
                view_all_requests()

            elif choice == "3":
                search_request()

            elif choice == "4":
                assign_request()

            elif choice == "5":
                close_existing_request()

            elif choice == "6":
                request_id = read_id()
                show_history(request_id)

            elif choice == "7":
                review_support_records()

            elif choice == "8":
                correct_request_resolution()

            elif choice == "9":
                print("\n" + generate_report())

            elif choice == "10":
                path = export_report()
                print(f"\nReport saved: {path}")

            elif choice == "0":
                print("\nExiting TOSS.")
                break

            else:
                print("\nInvalid menu option.")

        except ValueError as error:
            print(f"\nInput error: {error}")

        except KeyboardInterrupt:
            print("\nOperation cancelled.")

        except EOFError:
            print("\nInput closed. Exiting TOSS.")
            break


if __name__ == "__main__":
    main()

