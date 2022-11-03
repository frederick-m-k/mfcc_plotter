
import model
import view
from config import logging as logging

if __name__ == "__main__":
    logging.debug("Starting the controller")
    model.init_model()
    view.init_view()

    view.start_view()
