import cv2 as cv
import numpy as np


# Paint class implements an interactive OpenCV drawing/filtering GUI
class Paint:
    def __init__(self):
        # Load the original image and create a working copy
        self.original_img = cv.imread("Photos/Griffith.jpg")
        self.img = self.original_img

        # Create a color bar (short, wide) for color selection and menu display
        self.color_bar = np.zeros(
            (self.img.shape[0] // 10, self.img.shape[1], 3), dtype="uint8"
        )
        # Variables for currently selected color (RGB)
        self.r, self.g, self.b = 0, 0, 0
        # Mouse coordinates for drawing
        self.mouse_x, self.mouse_y = 0, 0

        # Drawing state: True if mouse is pressed, False otherwise
        self.draw_state = False
        self.line_weight = 1  # Thickness of drawing brush

        # Menu text for each mode
        self.menu_text = [
            "Select a Mode",
            "Draw: Select a color then left click hold to draw",
            "Filter: Select confirm, scroll through filters, press confirm again to apply",
            "Draw Squares: Choose color, confirm, draw squares, confirm with space. ESC to quit",
        ]
        # State variables for mode, filter, and confirmation
        self.mode_selection = 0
        self.confirm_selection = True
        self.filter_selection = 0

        # Map mode numbers to handler methods
        self.mode_handlers = {
            1: self.handle_drawing_mode,
            2: self.handle_filter_mode,
            3: self.handle_roi_mode,
        }

    def run(self):
        # Main event loop: create trackbars and handle user interaction
        self.create_trackbars()
        while True:
            self.display_gui(self.img)
            self.retrieve_trackbar_data()
            # Call the handler for the current mode
            handler = self.mode_handlers.get(
                self.mode_selection, self.handle_default_mode
            )
            print(self.mode_selection)
            handler()

            key = cv.waitKey(1)
            if key == ord("q"):
                break
        print("running")

    def display_gui(self, img):
        # Create and update the color bar with current color and menu text
        new_color_bar = np.zeros((img.shape[0] // 10, img.shape[1], 3), dtype="uint8")
        new_color_bar[:] = [self.b, self.g, self.r]

        # Display the current menu text on the color bar
        cv.putText(
            new_color_bar,
            self.menu_text[self.mode_selection],
            (100, 50),
            cv.FONT_HERSHEY_COMPLEX,
            1.0,
            (0, 255, 255),
            thickness=2,
        )
        # Stack color bar above the image and show in window
        combined_img = np.vstack((new_color_bar, img))
        cv.imshow("window", combined_img)

    def create_trackbars(self):
        # Create the main window and all trackbars for color, mode, filter, and confirmation
        cv.namedWindow("window", cv.WINDOW_AUTOSIZE)
        cv.createTrackbar("r", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("g", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("b", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("mode", "window", 0, 3, self.empty_callback)
        cv.createTrackbar("filter", "window", 0, 3, self.empty_callback)
        cv.createTrackbar("confirm", "window", 0, 1, self.empty_callback)

    def retrieve_trackbar_data(self):
        # Read the current values from all trackbars
        self.r = cv.getTrackbarPos("r", "window")
        self.g = cv.getTrackbarPos("g", "window")
        self.b = cv.getTrackbarPos("b", "window")
        self.mode_selection = cv.getTrackbarPos("mode", "window")
        self.filter_selection = cv.getTrackbarPos("filter", "window")
        self.confirm_selection = cv.getTrackbarPos("confirm", "window")

    def empty_callback(self):
        # Empty callback for trackbars that don't need to do anything on change
        pass

    def handle_drawing_mode(self):
        # Drawing mode: set mouse callback and draw on image if mouse is pressed
        cv.setMouseCallback("window", self.mouse_call_back)
        if self.draw_state == True:
            # Adjust y for color bar offset, then draw a square at (x, y)
            y = self.mouse_y - (
                self.color_bar.shape[0]
            )  # adjust the window so that the color bar doesn't offset the mouse
            x = self.mouse_x
            w = self.line_weight
            self.img[y - w : y + w, x - w : x + w, :] = [
                self.b,
                self.g,
                self.r,
            ]

    def mouse_call_back(self, event, x, y, flags, param):
        # Mouse callback for drawing mode: update draw state and mouse position
        if self.mode_selection == 1:
            if event == cv.EVENT_LBUTTONDOWN:
                self.draw_state = True
            if event == cv.EVENT_LBUTTONUP:
                self.draw_state = False
        self.mouse_x = x
        self.mouse_y = y

    def handle_filter_mode(self):
        # Filter mode: allow user to preview and confirm filter selection
        if self.confirm_selection == 1:
            cv.waitKey(100)
            cv.setTrackbarPos("confirm", "window", 0)
            self.retrieve_trackbar_data()
            print("confirm : ", self.confirm_selection)
            # Enter filter preview loop until user confirms
            while self.confirm_selection == 0:
                new_img = self.img.copy()
                self.retrieve_trackbar_data()
                if self.filter_selection == 1:
                    new_img = cv.cvtColor(self.img, cv.COLOR_BGR2HLS)
                elif self.filter_selection == 2:
                    new_img = cv.cvtColor(self.img, cv.COLOR_BGR2LAB)
                elif self.filter_selection == 3:
                    new_img = cv.cvtColor(self.img, cv.COLOR_BGR2LUV)
                self.display_gui(new_img)

                cv.waitKey(10)

            # Reset trackbars and update image with selected filter
            cv.setTrackbarPos("mode", "window", 0)
            cv.setTrackbarPos("filter", "window", 0)
            cv.setTrackbarPos("confirm", "window", 0)

            self.img = new_img

    def handle_roi_mode(self):
        # ROI mode: allow user to select and fill multiple ROIs with current color
        if self.confirm_selection == 1:
            cv.waitKey(100)
            cv.setTrackbarPos("confirm", "window", 0)
            rois_coords = cv.selectROIs("Select ROIS", self.img)
            for coords in rois_coords:
                for x, y, w, h in rois_coords:
                    roi_img = self.img[y : y + h, x : x + w, :]
                    roi_img[:] = [
                        self.b,
                        self.g,
                        self.r,
                    ]
                    self.img[y : y + h, x : x + w, :] = roi_img
            cv.setTrackbarPos("mode", "window", 0)

    def handle_default_mode(self):
        # Default handler for mode 0 (no action)
        pass


if __name__ == "__main__":
    # Entry point: create and run the Paint application
    painter = Paint()
    painter.run()
