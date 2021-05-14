# !/usr/bin/env python
# title           :view.py
# description     :Interface Mapping Class using OpenCV
# author          :Juan Maldonado
# date            :5/11/2021
# version         :0.0
# usage           :SEE README.md
# python_version  :3.7.10
# conda_version   :4.9.2
# ========================================================================================================
from mapping import ScreenMap
import cv2 as cv
# import pytesseract
import numpy as np
import time
import os
import argparse
import imutils

"""
The UIReader class helps map out the screen locations of interface widgets using OpenCV.
"""


class UIReader:
	def __init__(self):
		"""
		Constructor. Initializes video feed and configures appropriate directories (tentative).
		"""
		self.program_name = None  # To Do: Exception Handling
		self.page_name = None  # To Do: Exception Handling
		self.assets_directory = "/interface_assets/"  # Directory location of templates.
		self.gui_map = ScreenMap()  # Class of charge of tracking widgets identified by UIReader.
		self.capture_feed = cv.VideoCapture(0)  # Device (USB Capture Card) outputting video feed of program.
		self.source_filepath = None
		self.template_filepath = None

	def read_video_feed(self):
		"""
		Read one frame from the video feed (USB Capture Card) and write to file.
		"""
		ret, frame = self.capture_feed.read()
		cv.imshow("test?", frame)
		cv.waitKey(0)
		cv.imwrite("current_view.png", frame)

	def test_video_feed(self):
		"""
		Test video feed.
		"""
		if not self.capture_feed.isOpened():
			print("Cannot open camera")
			exit()

		while True:
			ret, frame = self.capture_feed.read()
			if not ret:
				break

			cv.imshow('Frame', frame)
			if cv.waitKey(1) == ord('q'):
				break
		self.capture_feed.release()
		cv.destroyAllWindows()

	def extract_text(self, filepath: str):
		"""
		Extract text from an image using Google Tesseract.
		"""
		start_time = time.time()
		image = cv.imread(filepath)
		print("Extracting Text From Image...")
		text = pytesseract.image_to_string(image=image)
		print(text)
		end_time = time.time()

		print("Elapsed Time: {}".format(end_time - start_time))

	def select_mapping_method(self, flag: str):
		"""
		Selects mapping method
		:param flag: Mapping method name. Options -> [TEMPLATE_MATCHING, FEATURE_MATCHING]
		"""
		if flag == "TEMPLATE_MATCHING":
			self.match_template()

		if flag == "FEATURE_MATCHING":
			print("Not implemented yet")
		else:
			print("Mapping Method Provided Not Found")

	def find_contours(self):
		image = cv.imread("vitals_camera.jpg")
		interface = cv.imread("home_page_root.jpg")
		interface_gray = cv.cvtColor(interface, cv.COLOR_BGR2GRAY)
		interface_result = interface.copy()
		ret1, thresh1 = cv.threshold(interface_gray, 127, 255, 0)
		contours = cv.findContours(thresh1.copy(), cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)
		contours = contours[0] if len(contours) == 2 else contours[1]

		cv.drawContours(interface_result, contours, -1, color=(0, 255, 0), thickness=3)

		cv.imshow("testy", thresh1)
		cv.imshow("testy", interface_result)
		cv.waitKey(0)

		"""
		img_gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
		result = image.copy()
		ret, threshold = cv.threshold(img_gray, 127, 255, 0)
		contours = cv.findContours(threshold, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
		contours = contours[0] if len(contours) == 2 else contours[1]
		# Grab largest contour
		big_contours = max(contours, key=cv.contourArea)
		cv.drawContours(image=result, contours=[big_contours], contourIdx=0, color=(0, 255, 0), thickness=3)
		x, y, w, h = cv.boundingRect(big_contours)
		cv.imshow("test?", result)
		cv.waitKey(0)
		"""

	def map_interface(self):
		print("Mapping Interface...")

	def match_template(self, flag: int):
		"""
		Search for widget in interface using template matching
		"""

		if flag == 0:
			start_time = time.time()
			interface_img = cv.imread("home_page_root.jpg")
			widget_img = cv.imread("vitals_camera.jpg")
			# Convert template image to Grayscale Coloring and it's threshold to binary
			partial_image = cv.cvtColor(widget_img, cv.COLOR_RGB2GRAY)
			partial_image = cv.threshold(partial_image, 0, 255, cv.THRESH_BINARY)[1]

			# Get contour from partial image
			contours = cv.findContours(partial_image.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
			contours = contours[0] if len(contours) == 2 else contours[1]
			# Grab largest contour
			big_contours = max(contours, key=cv.contourArea)

			# Build mask based off contour
			mask = np.zeros((widget_img.shape[0], widget_img.shape[1], 3), dtype=np.uint8)
			cv.drawContours(mask, [big_contours], 0, (255, 255, 255), 1)

			# Capture height and width of mask (necessary to bound detection boxes).
			hh, ww = mask.shape[:2]

			# Extract template from BGR image
			template = widget_img[:, :, 0:3]

			# Perform Template Matching
			correlation = cv.matchTemplate(image=interface_img, templ=template, method=cv.TM_CCORR_NORMED, mask=mask)
			min_val, max_val, min_loc, max_loc = cv.minMaxLoc(src=correlation)
			max_val_ncc = '{:3f}'.format(max_val)

			# Get coordinates of area in source that matched with template
			xx = max_loc[0]
			yy = max_loc[1]

			# Draw template bounds
			result = interface_img.copy()
			cv.rectangle(img=result, pt1=(xx, yy), pt2=(xx + ww, yy + hh), color=(0, 0, 255), thickness=1)

			cv.imshow('interface', interface_img)
			cv.imshow('widget', widget_img)
			cv.imshow('partial_img', partial_image)
			cv.imshow('mask', mask)
			cv.imshow('template', template)

			end_time = time.time()
			print("Elapsed Time: {}".format(end_time - start_time))
			cv.imshow('result', result)
			cv.waitKey(0)

		if flag == 1:
			start_time = time.time()
			image_dir = "interface_assets/steris/home_page/"  # TO DO: Temp make this dynamic
			interface_img = cv.imread("home_page_root.jpg")  # TO DO: Put this file somewhere else in the future.
			result = interface_img.copy()
			for image in os.listdir(image_dir):
				relative_path = os.path.join(image_dir, image)
				print("Finding: {}".format(image))
				widget_img = cv.imread(relative_path)

				# Convert template image to Grayscale Coloring and it's threshold to binary

				partial_image = cv.cvtColor(widget_img, cv.COLOR_RGB2GRAY)
				partial_image = cv.threshold(partial_image, 0, 255, cv.THRESH_BINARY)[1]

				# Get contour from partial image
				contours = cv.findContours(partial_image.copy(), cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
				contours = contours[0] if len(contours) == 2 else contours[1]
				# Grab largest contour
				big_contours = max(contours, key=cv.contourArea)

				# Build mask based off contour
				mask = np.zeros((widget_img.shape[0], widget_img.shape[1], 3), dtype=np.uint8)
				cv.drawContours(mask, [big_contours], 0, (255, 255, 255), 1)

				# Capture height and width of mask (necessary to bound detection boxes).
				hh, ww = mask.shape[:2]

				# Extract template from BGR image
				template = widget_img[:, :, 0:3]

				# Perform Template Matching
				correlation = cv.matchTemplate(image=interface_img, templ=template, method=cv.TM_CCORR_NORMED,
											   mask=mask)
				min_val, max_val, min_loc, max_loc = cv.minMaxLoc(src=correlation)
				max_val_ncc = '{:3f}'.format(max_val)

				# Get coordinates of area in source that matched with template
				xx = max_loc[0]
				yy = max_loc[1]

				# Draw template bounds

				cv.rectangle(img=result, pt1=(xx, yy), pt2=(xx + ww, yy + hh), color=(0, 0, 255), thickness=1)

			# Show results
			end_time = time.time()
			elapsed_timed = end_time - start_time
			print("Elapsed Time: {}s".format(elapsed_timed))
			print("Average Processing Time Per Template: {}s".format(elapsed_timed / len(os.listdir(image_dir))))

			cv.imshow("RESULT", result)
			cv.waitKey(0)

		if flag == 2:
			template = cv.imread("vitals_camera.jpg")
			image = cv.imread("home_page_root.jpg")
			result = image.copy()

			w, h = template.shape[:-1]

			templateGray = cv.cvtColor(template, cv.COLOR_BGR2GRAY)

			ret, mask = cv.threshold(templateGray, 200, 255, cv.THRESH_BINARY)

			mask_inv = cv.bitwise_not(mask)
			mask_inv = cv.cvtColor(mask_inv, cv.COLOR_GRAY2RGB)

			method = cv.TM_CCORR_NORMED

			correlation = cv.matchTemplate(image, template, method, None, mask=mask_inv)
			min_val, max_val, min_loc, max_loc = cv.minMaxLoc(src=correlation)
			max_val_ncc = '{:3f}'.format(max_val)

			# Get coordinates of area in source that matched with template
			xx = max_loc[0]
			yy = max_loc[1]

			cv.rectangle(img=result, pt1=(xx, yy), pt2=(xx + h, yy + w), color=(0, 0, 255), thickness=1)
			cv.imshow("RESULT", result)
			cv.waitKey(0)


def main():
	"""
	ap = argparse.ArgumentParser(description="Test Mapping Methods")
	ap.add_argument("--mapping_method", required=True, choices=["TEMPLATE_MATCHING", "FEATURE_MATCHING"],
					help="Mapping method used to locate widgets")
	ap.add_argument("--source", required=True, help="Source image where template matching will occur")
	ap.add_argument("--template", required=True, help="Template image that will be searched in source")
	args = vars(ap.parse_args())
	"""
	viewer = UIReader()
	viewer.find_contours()
	# viewer.match_template(2)
	# viewer.read_video_feed()

	"""
	viewer.source_filepath = args["source"]
	viewer.template_filepath = args["template"]
	viewer.select_mapping_method(args["mapping_method"])
	"""


if __name__ == "__main__":
	main()
