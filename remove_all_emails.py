from add_email import save_emails


def run():
    remove_all = input("Remove all saved emails? (y/n): ")

    if remove_all == "y":
        save_emails([])


if __name__ == "__main__":
    run()
