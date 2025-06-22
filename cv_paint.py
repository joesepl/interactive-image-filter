import cv2 as cv
import numpy as np


class Paint:
    def __init__(self):
        # Retrieve original image and make a working image as well for changes
        self.original_img = cv.imread("Photos/Griffith.jpg")
        self.img = self.original_img

        # Create an empty image with the same with but smaller height than the image
        self.color_bar = np.zeros(
            (self.img.shape[0] // 10, self.img.shape[1], 3), dtype="uint8"
        )
        # variables for selected colors
        self.r, self.g, self.b = 0, 0, 0
        # Mouse data for mouse callback to update
        self.mouse_x, self.mouse_y = 0, 0

        # Draw state used to keep track of when mouse is pressed then released. Since they are oneshot not maintained.
        self.draw_state = False
        self.line_weight = 1

        # Text to display per menu option
        self.menu_text = [
            "Select a Mode",
            "Draw: Select a color then left click hold to draw",
            "Filter: Select confirm, scroll through filters, press confirm again to apply",
            "Draw Squares: Choose color, confirm, draw squares, confirm with space. ESC to quit",
        ]
        # Variables to hold what mode and filter the user has selected and whether confirm has been selected.
        self.mode_selection = 0
        self.confirm_selection = True
        self.filter_selection = 0

        self.mode_handlers = {
            1: self.handle_drawing_mode,
            2: self.handle_filter_mode,
            3: self.handle_roi_mode,
        }

    def run(self):
        self.create_trackbars()
        while True:
            self.display_gui(self.img)
            self.retrieve_trackbar_data()
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
        new_color_bar = np.zeros((img.shape[0] // 10, img.shape[1], 3), dtype="uint8")
        new_color_bar[:] = [self.b, self.g, self.r]

        cv.putText(
            new_color_bar,
            self.menu_text[self.mode_selection],
            (100, 50),
            cv.FONT_HERSHEY_COMPLEX,
            1.0,
            (0, 255, 255),
            thickness=2,
        )
        combined_img = np.vstack((new_color_bar, img))
        cv.imshow("window", combined_img)

    def create_trackbars(self):
        cv.namedWindow("window", cv.WINDOW_AUTOSIZE)
        cv.createTrackbar("r", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("g", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("b", "window", 0, 255, self.empty_callback)
        cv.createTrackbar("mode", "window", 0, 3, self.empty_callback)
        cv.createTrackbar("filter", "window", 0, 3, self.empty_callback)
        cv.createTrackbar("confirm", "window", 0, 1, self.empty_callback)

    def retrieve_trackbar_data(self):
        self.r = cv.getTrackbarPos("r", "window")
        self.g = cv.getTrackbarPos("g", "window")
        self.b = cv.getTrackbarPos("b", "window")
        self.mode_selection = cv.getTrackbarPos("mode", "window")
        self.filter_selection = cv.getTrackbarPos("filter", "window")
        self.confirm_selection = cv.getTrackbarPos("confirm", "window")

    def empty_callback(self):
        # emtpy call back for callbacks we dont need.
        pass

    def handle_drawing_mode(self):
        cv.setMouseCallback("window", self.mouse_call_back)
        if self.draw_state == True:
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
        if self.mode_selection == 1:
            if event == cv.EVENT_LBUTTONDOWN:
                self.draw_state = True
            if event == cv.EVENT_LBUTTONUP:
                self.draw_state = False
        self.mouse_x = x
        self.mouse_y = y

    def handle_filter_mode(self):
        if self.confirm_selection == 1:
            cv.waitKey(100)
            cv.setTrackbarPos("confirm", "window", 0)
            self.retrieve_trackbar_data()
            print("confirm : ", self.confirm_selection)
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

            cv.setTrackbarPos("mode", "window", 0)
            cv.setTrackbarPos("filter", "window", 0)
            cv.setTrackbarPos("confirm", "window", 0)

            self.img = new_img

    def handle_roi_mode(self):
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
        pass


if __name__ == "__main__":
    painter = Paint()
    painter.run()
