import zenpy
import zipfile
import os
from dotenv import load_dotenv
from tqdm import tqdm

class Zendesk:
    """
    A class for interacting with Zendesk. The current implementation focuses on
    retrieving dental images from tickets.

    For initialization, the user needs either an email and a token to the requried views OR
    the user needs to have the ZENDESK_USER and ZENDESK_PWD environment variables set (via an .env file).
    """
    def __init__(self, email=None, token=None):
        load_dotenv()
        try:
            self.email = os.getenv("ZENDESK_USER")
            self.token = os.getenv("ZENDESK_PWD")
        except:
            self.email = email
            self.token = token
        credentials = {'email': self.email,
                        'token': self.token,
                        'subdomain': 'dansktandforsikring'}
        try:
            self.client = zenpy.Zenpy(**credentials)
            self.data_view = os.getenv("ZENDESK_VIEW")
        except:
            raise Exception("Invalid email or token")


    def retrieve_dental_images(self, ticket_id, root):
        """
        Scrapes the dental images from the comments of a ticket. Currrently only works
        for local storage.
        """
        # TODO: Add error handling
        # TODO: Add GCP bucket upload

        comments = self.client.tickets.comments(ticket_id)
        

        # Iterate through comments to find attachments
        for comment in comments:
            for attachment in comment.attachments:
                # Define the file path
                file_path = os.path.join(root, attachment.file_name)

                # Download the attachment
                if file_path.endswith(".zip"):
                    self.client.attachments.download(attachment_id=attachment.id, destination=file_path)
                    with zipfile.ZipFile(file_path, 'r') as zip_ref:
                        zip_ref.extractall(root)
                    os.remove(file_path)


    def get_view_tickets(self, view_id=None):
        """
        Retrieves all tickets from a view.
        """
        if view_id is None:
            view_id = self.data_view
        return self.client.views.tickets(view_id)
    

    def retrieve_all_image_data(self, root, break_after=None):
        """
        Retrieves all image data from all tickets in the view.
        """
        # TODO: Expand to GCP bucket upload

        tickets = self.get_view_tickets()

        for index, ticket in tqdm(enumerate(tickets)):

            # Break after a certain number of tickets
            if break_after is not None:
                if index > break_after:
                    print(f"Breaking after {break_after} tickets.")
                    break

            temp_root = os.path.join(root, f"{ticket.id}")

            if not os.path.exists(temp_root):
                os.makedirs(temp_root)
            else:
                print(f"Ticket {ticket.id} already exists in {root}.")
                continue
            self.retrieve_dental_images(ticket.id, temp_root)
            
            

if __name__ == "__main__":
    z = Zendesk()
    z.retrieve_all_image_data("data")
    
    # Example usage
    # z.retrieve_dental_images(123, "data")
    # z.retrieve_all_image_data("data", break_after=10)
    # z.get_view_tickets()
    # z.retrieve_dental_images(123, "data")
    
    