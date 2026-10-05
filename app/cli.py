import argparse
from app.services import reservation_service, resource_service, user_service
from app.database import Session
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(description="Slot Engine CLI")

    parser.add_argument("--start_date", type=datetime.fromisoformat)
    parser.add_argument("--end_date", type=datetime.fromisoformat)
    parser.add_argument("--user_id", type=int)
    parser.add_argument("--resource_id", type=int)
    parser.add_argument("--user_name")
    parser.add_argument("--resource_name")
    parser.add_argument("--reservation_id", type=int)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--reserve_slot", action="store_true")
    group.add_argument("--release_slot", action="store_true")
    group.add_argument("--list_reservations", action="store_true")
    group.add_argument("--update_slot", action="store_true")
    group.add_argument("--add_resource", action="store_true")
    group.add_argument("--remove_resource", action="store_true")
    group.add_argument("--list_resources", action="store_true")
    group.add_argument("--update_resource", action="store_true")
    group.add_argument("--add_user", action="store_true")
    group.add_argument("--remove_user", action="store_true")
    group.add_argument("--list_users", action="store_true")
    group.add_argument("--update_user", action="store_true")

    args = parser.parse_args()

    if args.add_user and args.user_name is None:
        parser.error("--add_user requires --user_name")

    if args.remove_user and args.user_id is None:
        parser.error("--remove_user requires --user_id")

    if args.update_user and (args.user_id is None or args.user_name is None):
        parser.error("--update_user requires --user_id and --user_name")

    if args.add_resource and args.resource_name is None:
        parser.error("--add_resource requires --resource_name")

    if args.remove_resource and args.resource_id is None:
        parser.error("--remove_resource requires --resource_id")

    if args.update_resource and (args.resource_id is None or args.resource_name is None):
        parser.error("--update_resource requires --resource_id and --resource_name")

    if args.reserve_slot and any(
        value is None for value in [args.user_id, args.resource_id, args.start_date, args.end_date]
    ):
        parser.error("--reserve_slot requires --user_id, --resource_id, --start_date, and --end_date")

    if args.release_slot and args.reservation_id is None:
        parser.error("--release_slot requires --reservation_id")

    if args.update_slot and any(
        value is None for value in [args.reservation_id, args.start_date, args.end_date]
    ):
        parser.error("--update_slot requires --reservation_id, --start_date, and --end_date")

    session = Session()

    try:
        if args.add_user:
            user = user_service.create_user(session, args.user_name)
            print(f"User created: {user.id}, {user.name}")

        elif args.remove_user:
            try:
                user_service.delete_user(session, args.user_id)
                print(f"User with ID {args.user_id} removed.")
            except ValueError as e:
                print(e)

        elif args.list_users:
            users = user_service.list_users(session)
            if not users:
                print("No users found.")
            else:
                for user in users:
                    print(f"User ID: {user.id}, Name: {user.name}")

        elif args.update_user:
            try:
                user = user_service.update_user(session, args.user_id, args.user_name)
                print(f"User updated: {user.id}, {user.name}")
            except ValueError as e:
                print(e)

        elif args.add_resource:
            resource = resource_service.create_resource(session, args.resource_name)
            print(f"Resource created: {resource.id}, {resource.name}")

        elif args.remove_resource:
            try:
                resource_service.delete_resource(session, args.resource_id)
                print(f"Resource with ID {args.resource_id} removed.")
            except ValueError as e:
                print(e)

        elif args.list_resources:
            resources = resource_service.list_resources(session)
            if not resources:
                print("No resources found.")
            else:
                for resource in resources:
                    print(f"Resource ID: {resource.id}, Name: {resource.name}")

        elif args.update_resource:
            try:
                resource = resource_service.update_resource(session, args.resource_id, args.resource_name)
                print(f"Resource updated: {resource.id}, {resource.name}")
            except ValueError as e:
                print(e)

        elif args.reserve_slot:
            try:
                reservation = reservation_service.create_reservation(
                    session, args.user_id, args.resource_id, args.start_date, args.end_date
                )
                print(f"Reservation created: {reservation.id}, User ID: {reservation.user_id}, Resource ID: {reservation.resource_id}, Start: {reservation.start}, End: {reservation.end}")
            except ValueError as e:
                print(e)

        elif args.release_slot:
            try:
                reservation_service.delete_reservation(session, args.reservation_id)
                print(f"Reservation with ID {args.reservation_id} released.")
            except ValueError as e:
                print(e)

        elif args.list_reservations:
            reservations = reservation_service.list_reservations(session)
            if not reservations:
                print("No reservations found.")
            else:
                for reservation in reservations:
                    print(f"Reservation ID: {reservation.id}, User ID: {reservation.user_id}, Resource ID: {reservation.resource_id}, Start: {reservation.start}, End: {reservation.end}")

        elif args.update_slot:
            try:
                reservation = reservation_service.update_reservation(session, args.reservation_id, args.start_date, args.end_date)
                print(f"Reservation updated: {reservation.id}, Resource ID: {reservation.resource_id}, Start: {reservation.start}, End: {reservation.end}")
            except ValueError as e:
                print(e)

    finally:
        session.close()