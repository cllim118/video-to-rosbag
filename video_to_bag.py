import os
import sys
import cv2
import rosbag
import rospy
from sensor_msgs.msg import Image
from cv_bridge import CvBridge

def video_to_bag(video_path, bag_path, topic="/cam0/image_raw", frame_rate=30):
    rospy.init_node('video_to_bag', anonymous=True)
    bridge = CvBridge()

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video {video_path}")
        return

    bag = rosbag.Bag(bag_path, 'w')

    try:
        count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            timestamp = rospy.Time.from_sec(count / frame_rate)
            ros_image = bridge.cv2_to_imgmsg(frame, encoding="bgr8")
            ros_image.header.stamp = timestamp
            bag.write(topic, ros_image, timestamp)
            count += 1

            if count % 100 == 0:
                print(f"Processed {count} frames from {video_path}")

    finally:
        bag.close()
        cap.release()
        print(f"Finished writing bag: {bag_path}")

def batch_convert_mp4_to_bag(input_folder, output_folder, frame_rate=30, topic="/cam0/image_raw"):
    # Make sure output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # List all mp4 files in the input folder
    mp4_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.mp4')]

    if not mp4_files:
        print(f"No .mp4 files found in {input_folder}")
        return

    for mp4_file in mp4_files:
        video_path = os.path.join(input_folder, mp4_file)
        bag_filename = os.path.splitext(mp4_file)[0] + '.bag'
        bag_path = os.path.join(output_folder, bag_filename)

        print(f"Converting {video_path} -> {bag_path}")
        video_to_bag(video_path, bag_path, topic=topic, frame_rate=frame_rate)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: batch_mp4_to_bag.py <input_folder> <output_folder> [frame_rate] [topic]")
        sys.exit(1)

    input_folder = sys.argv[1]
    output_folder = sys.argv[2]
    fps = float(sys.argv[3]) if len(sys.argv) > 3 else 30.0
    topic_name = sys.argv[4] if len(sys.argv) > 4 else "/cam0/image_raw"

    batch_convert_mp4_to_bag(input_folder, output_folder, frame_rate=fps, topic=topic_name)
