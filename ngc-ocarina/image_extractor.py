#!/usr/bin/python

# Import statements
import cv2
from datetime import datetime
import gc
import numpy as np
import os
import pandas as pd
import sqlite3
import yaml

def main():
    # Get config parameters
    try:
        with open("./config/config_image_extractor.yaml", "r") as stream:
            config = yaml.safe_load(stream)
    except:
        print(f"Error reading config file")
        return

    # Get trial list from config file
    trial_list = config["trial_list"]
    if trial_list is None or len(trial_list) == 0:
        print(f"Invalid trial_id")
        return

    # Get bounding box colors from config file
    color_dict = dict()
    for component in config["component_color"]:
        color_dict[component] = config["component_color"][component]

    # Extract configuration parameters
    database_path_base = config["database_path"]
    for subject_id, trial_id in trial_list:
        # Ensure database file exists
        database_path = database_path_base + \
            f"{subject_id}/{subject_id}_{trial_id}.sqlite"
        if not os.path.exists(database_path):
            print(f"Database file doesn't exist {database_path}")
            continue
        
        # Create output path
        output_path = database_path_base + f"{subject_id}/outputs"
        output_path = os.path.join(output_path, subject_id, str(trial_id))
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Gather image and video feeds to extract for this trial
        image_feeds_to_extract = []
        video_feeds_to_extract = []
        for feed in config["feeds"]:
            if config["feeds"][feed]["extract_images"]:
                image_feeds_to_extract.append(
                    (feed, config["feeds"][feed]["include_bbs"]))
            if config["feeds"][feed]["extract_video"]:
                video_feeds_to_extract.append(
                    (feed, config["feeds"][feed]["include_bbs"]))

        if len(image_feeds_to_extract) == 0 and len(video_feeds_to_extract) == 0:
            print("Nothing to extract, check config settings")
            continue      

        # Extract image feeds
        for image_feed in image_feeds_to_extract:
            print(
                f"Starting {image_feed[0]} image extraction for {subject_id}:{trial_id}")
            generate_images(
                database_path,
                output_path,
                trial_id,
                image_feed,
                chunk_size=config["chunk_size"],
                color_dict=color_dict)

        # Generate video feeds
        for video_feed in video_feeds_to_extract:
            print(
                f"Starting {video_feed[0]} video extraction for {subject_id}:{trial_id}")
            video_tuples = generate_videos(
                database_path,
                output_path,
                trial_id,
                video_feed,
                chunk_size=config["chunk_size"],
                color_dict=color_dict)

            if len(video_tuples) > 0:
                print(
                    f"Combining {video_feed[0]} video feeds for {subject_id}:{trial_id}")
                combine_videos(video_tuples, output_path, video_feed)

def generate_images(database_path, output_path, trial_id, image_feed, chunk_size=3000, color_dict=None):
    # Get database connection
    con = sqlite3.connect(database_path)

    # Extract image table and whether bounding boxes should be drawn
    image_table, bounding_boxes = image_feed

    # Get total image count
    if bounding_boxes:
        query = f"""SELECT COUNT(1)
                FROM {image_table} LEFT OUTER JOIN {image_table}_bounding_boxes USING (image_count);"""
    else:
        query = f"SELECT COUNT(1) FROM {image_table};"
    image_count = pd.read_sql_query(
        query, con).iloc[0][0]

    # Check for and create output path for this feed
    if not os.path.exists(os.path.join(output_path, image_table, "images")):
        os.makedirs(os.path.join(output_path, image_table, "images"))

    last_timestamp = None
    current_pointer = 0
    # Loop until full count is reached
    while current_pointer < image_count:
        time_list = []
        if current_pointer+chunk_size > image_count:
            chunk_size = image_count-current_pointer

        # Query for bounding box entries, if desired
        if bounding_boxes:
            print(f"Running image and bounds query {datetime.now()}")
            query = f"""SELECT {image_table}.*, {image_table}_bounding_boxes.component_id, {image_table}_bounding_boxes.bounds
                FROM {image_table} LEFT OUTER JOIN {image_table}_bounding_boxes USING (image_count)
                ORDER BY timestamp LIMIT {chunk_size} OFFSET {current_pointer};"""
            images_df = pd.read_sql_query(
                query,
                con)
        else:
            print(f"Running image query {datetime.now()}")
            query = f"SELECT * FROM {image_table} ORDER BY timestamp LIMIT {chunk_size} OFFSET {current_pointer};"
            images_df = pd.read_sql_query(
                query,
                con)

        # Write all images in chunk to file
        print(f"Parsing image chunk {datetime.now()}")
        id_group = images_df.groupby(["image_count"])
        for _, grouping in id_group:
            # Extract image data and convert to cv2 object
            image_row = grouping.iloc[0]
            dt = np.dtype(np.uint8)
            dt = dt.newbyteorder(">" if bool(image_row.is_bigendian) else "<")
            num_channels = 4 if image_row.encoding == "bgra8" else 1
            image_data = np.frombuffer(image_row.data, dtype=dt)
            if num_channels == 4:
                image_data = np.reshape(
                    image_data, (int(image_row.height), int(image_row.width), num_channels))
                image_data = image_data[:, :, 0:3]
                image_data = np.reshape(
                    image_data, (int(image_row.height), int(image_row.width), 3))
            else:
                image_data = np.reshape(
                    image_data, (int(image_row.width), int(image_row.height)))
                image_data = np.stack((image_data,)*3, axis=-1)

            # Draw bounding boxes on image
            if bounding_boxes:
                for _, row in grouping.iterrows():
                    if row.bounds != None:
                        bounds = np.frombuffer(row.bounds, dtype=np.int64)
                        bounds = bounds.reshape(((int)(len(bounds)/2), 2))
                        color = (255, 0, 0)
                        if color_dict is not None:
                            color = color_dict[row.component_id]

                        image_data = draw_component(
                            image_data,
                            bounds,
                            color=color)

            # Create image file title
            current_timestamp = datetime.strptime(
                image_row.timestamp, "%Y-%m-%d %H:%M:%S.%f")
            current_timestamp_str = datetime.strftime(
                current_timestamp, "%Y-%m-%d_%H:%M:%S.%f")

            title = f"{image_row.image_count}_{current_timestamp_str}.png"
            title = title.replace(":", "_")
            path_to_image = os.path.join(output_path, image_table,
                                         "images", title)

            if last_timestamp != None:
                time_diff_seconds = (current_timestamp -
                                     last_timestamp).total_seconds()
                time_list.append(f"duration {time_diff_seconds}")

            time_list.append(f"file {path_to_image}")
            last_timestamp = current_timestamp

            # Write image to file
            if not cv2.imwrite(path_to_image, image_data):
                raise Exception(
                    f"Failed to write image at path: {path_to_image}")

        current_pointer += chunk_size

        print(f"Writing second table {datetime.now()}")
        with open(os.path.join(output_path,
                            image_table,
                            "images",
                            f"{image_table}_timecodes.txt"), "a") as f:
            for line in time_list:
                f.write(f"{line}\n")
        
        # Cleanup for memory management
        del images_df, time_list
        gc.collect()

def generate_videos(database_path, output_path, trial_id, image_feed, chunk_size=3000, rgb_fps=30, vlc_fps=5, color_dict=None):
    # Get database connection
    con = sqlite3.connect(database_path)

    # Extract image table and whether bounding boxes should be drawn
    image_table, bounding_boxes = image_feed

    # Get total image count
    if bounding_boxes:
        query = f"""SELECT COUNT(1)
                FROM {image_table} LEFT OUTER JOIN {image_table}_bounding_boxes USING (image_count);"""
    else:
        query = f"SELECT COUNT(1) FROM {image_table};"
    image_count = pd.read_sql_query(
        query, con).iloc[0][0]

    # Check for and create output path
    if not os.path.exists(os.path.join(output_path, image_table, "videos")):
        os.makedirs(os.path.join(output_path, image_table, "videos"))

    current_pointer = 0
    milisecond_list = []
    video_tuples = []
    orig_dt_obj = None
    loop_counter = 1
    # Loop until full count is reached
    while current_pointer < image_count:
        if current_pointer+chunk_size > image_count:
            chunk_size = image_count-current_pointer

        # Query for bounding box entries, if desired
        if bounding_boxes:
            print(f"Running image and bounds query {datetime.now()}")
            query = f"""SELECT {image_table}.*, {image_table}_bounding_boxes.component_id, {image_table}_bounding_boxes.bounds
                FROM {image_table} LEFT OUTER JOIN {image_table}_bounding_boxes USING (image_count)
                ORDER BY timestamp LIMIT {chunk_size} OFFSET {current_pointer};"""
            images_df = pd.read_sql_query(
                query,
                con)
        else:
            print(f"Running image query {datetime.now()}")
            query = f"SELECT * FROM {image_table} ORDER BY timestamp LIMIT {chunk_size} OFFSET {current_pointer};"
            images_df = pd.read_sql_query(
                query,
                con)

        # Add all image data to a list
        print(f"Parsing image df {datetime.now()}")
        images = []
        fps = 30
        id_group = images_df.groupby(["image_count"])
        for _, grouping in id_group:
            # Extract frame data and convert to cv2 object
            image_row = grouping.iloc[0]

            dt = np.dtype(np.uint8)
            dt = dt.newbyteorder(">" if bool(image_row.is_bigendian) else "<")
            num_channels = 4 if image_row.encoding == "bgra8" else 1
            image_data = np.frombuffer(image_row.data, dtype=dt)
            if num_channels == 4:
                fps = rgb_fps
                image_data = np.reshape(
                    image_data, (int(image_row.height), int(image_row.width), num_channels))
                image_data = image_data[:, :, 0:3]
                image_data = np.reshape(
                    image_data, (int(image_row.height), int(image_row.width), 3))
            else:
                fps = vlc_fps
                image_data = np.reshape(
                    image_data, (int(image_row.width), int(image_row.height)))
                image_data = np.stack((image_data,)*3, axis=-1)

            # Draw bounding boxes on frame
            if bounding_boxes:
                for _, row in grouping.iterrows():
                    if row.bounds != None:
                        bounds = np.frombuffer(row.bounds, dtype=np.int64)
                        bounds = bounds.reshape(((int)(len(bounds)/2), 2))
                        color = (255, 0, 0)
                        if color_dict is not None:
                            color = color_dict[row.component_id]

                        image_data = draw_component(
                            image_data,
                            bounds,
                            color=color)

            current_timestamp = datetime.strptime(
                image_row.timestamp, "%Y-%m-%d %H:%M:%S.%f")
            if orig_dt_obj is None:
                orig_dt_obj = current_timestamp

            time_diff_seconds = (current_timestamp -
                                 orig_dt_obj).total_seconds()
            time_diff_miliseconds = time_diff_seconds * 1000
            milisecond_list.append(time_diff_miliseconds)

            images.append(image_data)
      
        print(f"Writing video chunk {loop_counter} {datetime.now()}")
        video_path = os.path.join(
            output_path, image_table, "videos", f"{image_table}_{loop_counter}.mp4")
        height, width, channels = images[-1].shape
        resolution = (int(width), int(height))
        video_writer = cv2.VideoWriter(
            video_path,
            cv2.VideoWriter_fourcc(*"mp4v"),
            fps,
            resolution,
            isColor=True)

        for image in images:
            video_writer.write(image)
        video_writer.release()

        video_tuples.append((video_path, fps, resolution))
        current_pointer += chunk_size
        loop_counter += 1

        del images_df, images, video_writer
        gc.collect()

    print(f"Writing milisecond table {datetime.now()}")
    with open(os.path.join(output_path, image_table, f"{image_table}_timecodes.txt"), "w") as f:
        for line in milisecond_list:
            f.write(f"{line}\n")

    return video_tuples

def draw_component(
        image,
        bounds,
        color=(0, 0, 0)):

    new_bounding_image = np.array(image)
    y, x = np.split(bounds, [-1], axis=1)
    new_bounding_image[y, x] = color

    return new_bounding_image

def combine_videos(video_tuples, output_path, image_feed):
    image_table, _ = image_feed

    final_video_path = os.path.join(
        output_path, image_table, f"{image_table}.mp4")

    fps = video_tuples[0][1]
    resolution = video_tuples[0][2]

    # Create a new video
    video = cv2.VideoWriter(
        final_video_path,
        cv2.VideoWriter_fourcc(*"mp4v"),
        fps,
        resolution,
        isColor=True)

    # Write all the frames sequentially to the new video
    for video_tupple in video_tuples:
        video_path, _, _ = video_tupple
        current_video = cv2.VideoCapture(video_path)
        while current_video.isOpened():
            # Get return value and curr frame of current video
            r, frame = current_video.read()
            if not r:
                break
            video.write(frame)          # Write the frame

    video.release()

# Main entry
if __name__ == "__main__":
    main()
