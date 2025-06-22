import cv2 as cv
import numpy as np

modes = "mode"
mouse_x = 0
mouse_y = 0
draw_state = False
# cv.imshow("Griffith", img)
line_wght = 1
draw_states = {
    "draw_state": draw_state,
    "mouse_x": mouse_x,
    "mouse_y": mouse_y,
}
menu_text = [
    "Select a Mode",
    "Draw: Select a color then left click hold to draw",
    "Filter: Select confirm, scroll through filters, press confirm again to apply",
    "Draw Squares: Choose color, confirm, draw squares, confirm with space. ESC to quit",
]
# Create a window that will be referred to by its name.


def main():
    orig_img = cv.imread("Photos/Griffith.jpg")
    img = orig_img
    # Create a blank picture to show current color selection
    color_bar = np.zeros((img.shape[0], img.shape[1] // 10, 3), dtype="uint8")
    # Create a window and the RGB track Bars
    cv.namedWindow("window", cv.WINDOW_AUTOSIZE)
    cv.createTrackbar("r", "window", 0, 255, nothing)
    cv.createTrackbar("g", "window", 0, 255, nothing)
    cv.createTrackbar("b", "window", 0, 255, nothing)
    cv.createTrackbar(modes, "window", 0, 3, nothing)
    cv.createTrackbar("confirm", "window", 0, 1, nothing)
    cv.createTrackbar("filter", "window", 0, 3, nothing)
    # ensure color bar and image dimesnions match for stacking later.

    # rois_select_colors(img, 255, 0, 0)
    while True:
        r, g, b = get_color_vals()
        mode_choice = cv.getTrackbarPos(modes, "window")
        color_bar = update_color_bar(img, menu_text, mode_choice, r, g, b)
        combined_img = np.vstack((color_bar, img))
        cv.imshow("window", combined_img)
        confirm = cv.getTrackbarPos("confirm", "window")
        if mode_choice == 1:
            # Need to create a mutable object. Mutable objects pass their handle. So when i pass draw state into mouse params it updates everywhere.

            mouse_params = {
                "mode_choice": mode_choice,
                "img": img,
                "draw_states": draw_states,
            }
            cv.setMouseCallback("window", mouse_call_back, param=mouse_params)
            print(draw_states["draw_state"])

            if draw_states["draw_state"] == True:
                img = draw(
                    img,
                    color_bar,
                    draw_states["mouse_x"],
                    draw_states["mouse_y"],
                    r,
                    g,
                    b,
                )
        elif mode_choice == 2 and confirm:
            # filter
            img = filter_image(color_bar, img)
            print("filter chosen")
        elif mode_choice == 3 and confirm:
            print("menu choice : ROI")
            img = rois_select_colors(img, r, g, b)

        cv.setTrackbarPos("confirm", "window", 0)
        combined_img = np.vstack((color_bar, img))
        cv.imshow("window", combined_img)

        # Poll GUI and quit if q
        key = cv.waitKey(1)
        if key == ord("q"):
            break


def draw(img, color_bar, x, y, r, g, b):
    print(f"Drawing at {x},{y}, the colors {r},{g},{b}")
    y = y - (color_bar.shape[0])
    img[y - line_wght : y + line_wght, x - line_wght : x + line_wght, :] = [
        b,
        g,
        r,
    ]
    return img


def mouse_call_back(event, x, y, flags, params):
    mode_choice = params["mode_choice"]
    if mode_choice == 1:
        if event == cv.EVENT_LBUTTONDOWN:
            print("mouse button down!")
            params["draw_states"]["draw_state"] = True
        if event == cv.EVENT_LBUTTONUP:
            params["draw_states"]["draw_state"] = False

        params["draw_states"]["mouse_x"] = x
        params["draw_states"]["mouse_y"] = y


def filter_image(color_bar, img):
    cv.setTrackbarPos("confirm", "window", 0)
    confirm = cv.getTrackbarPos("confirm", "window")
    while confirm == 0:
        new_img = img.copy()
        filter_selection = cv.getTrackbarPos("filter", "window")
        if filter_selection == 1:
            new_img = cv.cvtColor(img, cv.COLOR_BGR2HLS)
        elif filter_selection == 2:
            new_img = cv.cvtColor(img, cv.COLOR_BGR2LAB)
        elif filter_selection == 3:
            new_img = cv.cvtColor(img, cv.COLOR_BGR2LUV)
        confirm = cv.getTrackbarPos("confirm", "window")
        combined_img = np.vstack((color_bar, new_img))
        cv.imshow("window", combined_img)
        cv.waitKey(10)
    cv.setTrackbarPos(modes, "window", 0)
    cv.setTrackbarPos("filter", "window", 0)
    return new_img


def get_color_vals():
    r = cv.getTrackbarPos("r", "window")
    g = cv.getTrackbarPos("g", "window")
    b = cv.getTrackbarPos("b", "window")
    return r, g, b


def update_color_bar(img, menu_text, mode, r, g, b):
    new_color_bar = np.zeros((img.shape[0] // 10, img.shape[1], 3), dtype="uint8")
    new_color_bar[:, :, 0] = int(b)
    new_color_bar[:, :, 1] = int(g)
    new_color_bar[:, :, 2] = int(r)

    cv.putText(
        new_color_bar,
        menu_text[mode],
        (100, 50),
        cv.FONT_HERSHEY_COMPLEX,
        1.0,
        (0, 255, 255),
        thickness=2,
    )
    return new_color_bar


def rois_select_colors(img, r, g, b):
    print("ROIs entered")
    rois_coords = cv.selectROIs("Select ROIS", img, showCrosshair=True)
    for coords in rois_coords:
        for x, y, w, h in rois_coords:
            roi_img = img[y : y + h, x : x + w, :]
            roi_img[:] = [
                b,
                g,
                r,
            ]  # this weird slice says that for every page, row, and colum fill with these values.
            print(roi_img.shape)
            print(img.shape)
            img = overlay_image(img, roi_img, x, y, w, h)
    return img


# Take an overlay image and overlay it on the base image at the desired coordinates.
def overlay_image(img, overlay_img, x, y, w, h):
    img[y : y + h, x : x + w, :] = overlay_img
    return img


def nothing():
    pass


if __name__ == "__main__":
    main()
