from database import initialize
from requests import (
    PRIORITIES, STATUSES,
    create_request, list_requests,
    get_request, update_request, close_request
)


def show_request(record):
    if record is None:
        print("\nRequest not found.")
        return

    print(f"\nRequest: SR-{record['id']:04d}")
    print(f"Title: {record['title']}")
    print(f"Category: {record['category']}")
    print(f"Priority: {record['priority']}")
    print(f"Status: {record['status']}")
    print(f"Assigned to: {record['assigned_to']}")
    print(f"Created: {record['created_at']}")
    print(f"Resolution: {record['resolution'] or 'Not provided'}")


def read_id():
    return int(input("Request number: ").strip())


def main():
    initialize()

    while True:
        print("\n" + "=" * 42)
        print(" TECHNICAL OPERATIONS SUPPORT SYSTEM")
        print("=" * 42)
        print("[1] Create Request")
        print("[2] View All Requests")
        print("[3] Search Request")
        print("[4] Update / Assign Request")
        print("[5] Close Request")
        print("[0] Exit")

        choice = input("\nSelect option: ").strip()

        try:
            if choice == "1":
                title = input("Issue / Request: ")
                category = input("Category: ")
                print("Priorities:", ", ".join(PRIORITIES))
                priority = input("Priority: ").strip().title()

                request_id = create_request(
                    title, category, priority
                )
                print(f"\nCreated request SR-{request_id:04d}")

            elif choice == "2":
                records = list_requests()
                if not records:
                    print("\nNo requests found.")

                for record in records:
                    print(
                        f"SR-{record['id']:04d} | "
                        f"{record['priority']} | "
                        f"{record['status']} | "
                        f"{record['title']}"
                    )

            elif choice == "3":
                show_request(get_request(read_id()))

            elif choice == "4":
                request_id = read_id()
                print("Statuses:", ", ".join(STATUSES))
                status = input("New status: ").strip().title()
                assigned = input("Assigned to: ")

                if update_request(request_id, status, assigned):
                    print("Request updated.")
                else:
                    print("Request not found.")

            elif choice == "5":
                request_id = read_id()
                resolution = input("Resolution notes: ")

                if close_request(request_id, resolution):
                    print("Request closed.")
                else:
                    print("Request not found.")

            elif choice == "0":
                print("Exiting TOSS.")
                break

            else:
                print("Invalid menu option.")

        except ValueError as error:
            print(f"Input error: {error}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")


if __name__ == "__main__":
    main()
