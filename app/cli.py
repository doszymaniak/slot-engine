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

    parser.add_argument("--reserve_slot", action="store_true")
    parser.add_argument("--release_slot", action="store_true")
    parser.add_argument("--list_reservations", action="store_true")
    parser.add_argument("--add_resource", action="store_true")
    parser.add_argument("--remove_resource", action="store_true")
    parser.add_argument("--list_resources", action="store_true")
    parser.add_argument("--add_user", action="store_true")
    parser.add_argument("--remove_user", action="store_true")
    parser.add_argument("--list_users", action="store_true")

    args = parser.parse_args()
    session = Session()

    try:
        if args.add_user:
            if args.user_name is None:
                print("User name is required to add a user.")
                return
            user = user_service.create_user(session, args.user_name)
            print(f"User created: {user.id}, {user.name}")

        elif args.remove_user:
            if args.user_id is None:
                print("User ID is required to remove a user.")
                return
            try:
                user_service.delete_user(session,args.user_id)
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

        elif args.add_resource:
            if args.resource_name is None:
                print("Resource name is required to add a resource.")
                return
            resource = resource_service.create_resource(session, args.resource_name)
            print(f"Resource created: {resource.id}, {resource.name}")

        elif args.remove_resource:
            if args.resource_id is None:
                print("Resource ID is required to remove a resource.")
                return
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

        elif args.reserve_slot:
            if any(value is None for value in [args.user_id, args.resource_id, args.start_date, args.end_date]):
                print("User ID, Resource ID, Start Date, and End Date are required to reserve a slot.")
                return
            try:
                reservation = reservation_service.create_reservation(
                    session, args.user_id, args.resource_id, args.start_date, args.end_date
                )
                print(f"Reservation created: {reservation.id}, User ID: {reservation.user_id}, Resource ID: {reservation.resource_id}, Start: {reservation.start}, End: {reservation.end}")
            except ValueError as e:
                print(e)

        elif args.release_slot:
            if args.reservation_id is None:
                print("Reservation ID is required to release a slot.")
                return
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

    finally:
        session.close()