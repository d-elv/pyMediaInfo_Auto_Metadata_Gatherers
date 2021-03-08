from pymediainfo import MediaInfo
import datetime
import re
import os
import io

LOG_DIRECTORY = "\\\\10.10.52.250\\dropzone\\CTA\\08 PYTHON PROGRAMS\\02_PYMEDIAINFO\\LOGGED_OUTPUT"
text_file_underscores = "_" * 50

print("""Hello! This is PyMediaInfo. Please drag in either a single file or a folder
to scan the metadata of that single file or all files within that folder respectively.

Each file's metadata will be formatted and written to a text file ready to be sent on to producers.

This program will loop endlessly, simply close it once you're finished.

If this program closes and you didn't tell it to, it has likely crashed
due to an error with a file you're trying to scan.
If you encounter any issues, raise them to Dan and explain what happened.""")

single_dig_pattern = re.compile(r'\.[0-9]')
illegal_apostrophe = re.compile(r"'")
illegal_quotes = re.compile(r'"')
ghost_file_pattern = re.compile(r'^(\.)[<>-_.,+!?£$%^&*a-zA-Z0-9]*')
file_path_pattern = re.compile(r"(\w:\/?([^\\\/]*[\\\/])*)([^\\\/]+)$")
file_path_pattern_ending_backslash = re.compile(r"(\w:\/?([^\\\/]*[\\\/])*)([^\\\/]+)([\\\/]??)$")
accepted_file_types = [
                    '.mov', 
                    '.mxf', 
                    '.avi', 
                    '.wav', 
                    '.mp3', 
                    '.mp4', 
                    '.jpg', 
                    '.tif', 
                    '.tiff', 
                    '.aif', 
                    '.aiff', 
                    '.png', 
                    '.jpeg', 
                    '.tiff', 
                    '.wmv', 
                    '.mkv',
                    '.m4v',
                    '.dng',
                    '.r3d',
                    ]


def get_date():
    from datetime import datetime
    today = datetime.today().strftime('%Y%m%d')
    today = today[2:]
    return today


def format_file_size(file_size):
    # formats file sizes from bytes so that they are easily readable
    if file_size > 1000000000:
        file_size = file_size / 1000000000
        file_size = str(file_size)
        file_size = file_size[:6] + "GB"
    elif file_size > 1000000:
        file_size = file_size / 1000000
        file_size = str(file_size)
        file_size = file_size[:6] + " MB"
    elif file_size > 1000:
        file_size = file_size / 1000
        file_size = str(file_size) + " KB"
    elif file_size < 1000:
        file_size = str(file_size) + " Bytes"

    return file_size


def format_milliseconds(file_duration_seconds):
    # formats duration from milliseconds to hours, minutes, seconds
    file_duration_milli = file_duration_seconds / 1000
    file_duration_milli = str(file_duration_milli)[-2:]
    
    if file_duration_milli == '.0':
        pass
    if single_dig_pattern.match(file_duration_milli):
        file_duration_milli = file_duration_milli + "0"
    else:
        file_duration_milli = '.' + str(file_duration_milli)
    
    file_duration_seconds = file_duration_seconds / 1000
    file_duration_seconds = int(file_duration_seconds)
    file_duration_formatted = str(datetime.timedelta(seconds=file_duration_seconds))
    file_duration_formatted = str(file_duration_formatted) + file_duration_milli

    hours = file_duration_formatted.split(":")
    hours = str(hours)[0]
    if len(hours) == 1:
        hours = "0"
    
    file_duration_formatted = hours + file_duration_formatted
        
    return file_duration_formatted


def format_bit_rate(bit_rate_calculated):
    bit_rate_length = (len(str(bit_rate_calculated)))
    if "." in str(bit_rate_calculated):
        full_stop_index = str(bit_rate_calculated).index(".")
        if "." in str(bit_rate_calculated) and full_stop_index == 1 and bit_rate_length == 4:
            return str(bit_rate_calculated)
        amount_to_subtract = bit_rate_length - (full_stop_index + 3)
        bit_rate_formatted = str(bit_rate_calculated)[:-amount_to_subtract]
        return str(bit_rate_formatted)
    else:
        return str(bit_rate_calculated)


def calculate_bit_rate(bit_rate_raw):
    if bit_rate_raw < (1000 * 1000):
        bit_rate_calculated = bit_rate_raw / 1000
        bit_rate_formatted = format_bit_rate(bit_rate_calculated)
        bit_rate_formatted = bit_rate_formatted + " KB/s"
    if bit_rate_raw > (1000 * 1000):
        bit_rate_calculated = bit_rate_raw / (1000 * 1000)
        bit_rate_formatted = format_bit_rate(bit_rate_calculated)
        bit_rate_formatted = bit_rate_formatted + " MB/s"
    return bit_rate_formatted


def format_aspect_ratio(raw_aspect_ratio):
    formatted_aspect_ratio = ""
    if raw_aspect_ratio == "1.778":
        formatted_aspect_ratio = "16x9"
    elif raw_aspect_ratio == "1.000":
        formatted_aspect_ratio = "1x1"
    elif raw_aspect_ratio == "1.875":
        formatted_aspect_ratio = "Letterboxed 16:9"
    elif raw_aspect_ratio == "0.800":
        formatted_aspect_ratio = "4x5"
    elif raw_aspect_ratio == "0.563":
        formatted_aspect_ratio = "9x16"
    elif raw_aspect_ratio == "1.896":
        formatted_aspect_ratio = "2x1"
    if formatted_aspect_ratio == "":
        return raw_aspect_ratio
    else:
        return formatted_aspect_ratio


def get_root_length(input_directory):
    # Gets the root length of the directory given for scanning,
    # This is later used to ensure no sub folders are scanned.
    if os.path.isfile(input_directory):
        root_splitter = input_directory.split("\\")
        folder_name_for_output_file = root_splitter[-1]
        root_length = len(root_splitter)
        return root_length, folder_name_for_output_file

    for root, dir_path, files in os.walk(input_directory):
        root_splitter = root.split("\\")
        folder_name_for_output_file = root_splitter[-1]
        root_length = len(root_splitter)
        return root_length, folder_name_for_output_file


def get_file_name(input_file):
    name = input_file
    name = name.replace("\\", "/")
    name = name.split("/")
    if name[-1] == "":
        del name[-1]
    name = name[-1]
    if os.path.isfile(name):
        name, ext = os.path.splitext(name)
        return name
    return name


def write_log(complete_metadata_to_file_list):
    os.chdir(LOG_DIRECTORY)

    with io.open(name_for_output_file + "_MediaInfo_Output.txt", "w", encoding="utf8") as log_file:
    # with open(name_for_output_file + "_MediaInfo_Output.txt", "w" ) as log_file:     
        for file in complete_metadata_to_file_list:
            for attribute in file:
                log_file.write(str(attribute))
                log_file.write("\n")
            log_file.write(text_file_underscores)
            log_file.write("\n" * 2)

    length = len(complete_metadata_to_file_list)
    if length > 1:    
        with open(name_for_output_file + "_MediaInfo_Output.txt", "a") as log_file:
            log_file.write("Total files in selection: " + str(file_count) + "\n")
            log_file.write("Total errors in selection: " + str(error_count) + "\n")
    


def get_file_metadata(input_file):
    metadata_to_file_list = []
    name = get_file_name(input_file)
    print(f"Gathering metadata of... {name} ")
    try:
        media_info = MediaInfo.parse(input_file)
    except FileNotFoundError:
        print("Your file path is incorrect or your filename ", end="")
        print("is missing its extension, please try again.")
        metadata_to_file_list.append(f"File path for {name} was incorrect.")
        metadata_to_file_list.append("or was missing its extension. Error.")
        return metadata_to_file_list
    
    deep_metadata_list = []
    # simplified_file_list = []
    audio_channel_layout_list = []
    audio_channels = []
    audio_track_counter = 0
    image_track_present = False
    video_track_present = False
    audio_track_present = False

    for track in media_info.tracks:
        if track.track_type == "General":

            file_name = get_file_name(track.complete_name)
            file_path = track.complete_name
            file_size_raw = track.file_size

            # Checks if file is empty.
            if track.file_size == 0 or track.file_size == None:
                print(f"{file_name} is a corrupt file, please ", end="")
                print(f"investigate, resupply and try scanning again.")
                metadata_to_file_list.append(f"{file_name} is a corrupt file. Please resupply and rescan.")
                metadata_to_file_list.append(f"Error")
                return metadata_to_file_list
            else:
                pass

            file_duration_seconds = track.duration
            if file_duration_seconds == None:
                pass
            else:
                file_duration_formatted = format_milliseconds(file_duration_seconds)
            file_size_formatted = format_file_size(file_size_raw)

            today = get_date()
            metadata_to_file_list.append(f"FILE NAME: {file_name}") 
            metadata_to_file_list.append(f"RECEIVED DATE: {today}")
            metadata_to_file_list.append("RECEIVED VIA: Download")
            metadata_to_file_list.append(f"SOURCE LOCATION: {file_path}")
            metadata_to_file_list.append("BIN LOCATION: ")
            metadata_to_file_list.append(" ")
            metadata_to_file_list.append("*source details*")


        elif track.track_type == "Image":
            image_format = track.format
            image_width = track.width
            image_height = track.height
            image_colour_space = track.color_space
            image_bit_depth = track.bit_depth
            image_dimensions = (f"{image_width}x{image_height}")

            metadata_to_file_list.append(f"IMAGE FORMAT: {image_format}")
            metadata_to_file_list.append(f"IMAGE SIZE: {image_dimensions}")
            metadata_to_file_list.append(f"COLOUR SPACE: {image_colour_space}")
            metadata_to_file_list.append(f"BIT DEPTH: {image_bit_depth}")

            image_track_present = True

        elif track.track_type == "Video":
            
            aspect_ratio = format_aspect_ratio(track.display_aspect_ratio)

            video_width = track.width
            video_height = track.height
            frame_size = (f"{video_width}x{video_height}")
            colour_space = (f"{track.color_space} {track.color_primaries}")
            try:
                bit_rate = calculate_bit_rate(track.bit_rate)
            except:
                bit_rate = "Could not acquire Bit Rate"

            if track.frame_rate == None:
                frame_rate = track.original_frame_rate
            else:
                frame_rate = track.frame_rate

            if track.format_profile == None:
                format_profile = track.codec_id
            else:
                format_profile = track.format_profile
            
            video_codec = track.format

            metadata_to_file_list.append(f"VIDEO CODEC: {video_codec}")
            if video_codec == "Prores":
                metadata_to_file_list.append(f"VIDEO FORMAT PROFILE: {format_profile}")
            else:
                pass
            metadata_to_file_list.append(f"FILE SIZE: {file_size_formatted}")
            if file_duration_seconds == None:
                pass
            else:
                metadata_to_file_list.append(f"DURATION: {file_duration_formatted}")
            metadata_to_file_list.append(f"FRAME SIZE: {frame_size}")
            metadata_to_file_list.append(f"ASPECT RATIO: {aspect_ratio}")
            if frame_rate == None:
                pass
            else:
                metadata_to_file_list.append(f"FRAME RATE: {frame_rate}")
            if bit_rate == "Could not acquire Bit Rate":
                pass
            else:
                metadata_to_file_list.append(f"BIT RATE: {bit_rate}")

            video_track_present = True
        elif track.track_type == "Audio":
            audio_codec = track.format
            sample_rate = track.sampling_rate
            audio_channel_layout = track.audio_channel_layout
            audio_channels.append(track.channel_s)
            audio_channel_layout_list.append(audio_channel_layout)

            audio_track_counter += 1
            audio_track_present = True
            if audio_track_counter > 1:
                continue


    audio_channels = str(audio_channels)[1:-1]

    if audio_track_counter == 0:
        metadata_to_file_list.append(f"EMBEDDED AUDIO: None Present")
    else:    
        metadata_to_file_list.append(f"EMBEDDED AUDIO CHANNELS: {audio_track_counter}")
        metadata_to_file_list.append(f"EMBEDDED AUDIO TRACKS PER CHANNEL, IN ORDER: {audio_channels}")

    if len(audio_channel_layout_list) > 0 and None not in audio_channel_layout_list:
        metadata_to_file_list.append(f"EMBEDDED TRACK LAYOUT: {audio_channel_layout_list}")    

    if image_track_present == True or video_track_present == False:
        pass
    else:
        metadata_to_file_list.append("TEXTED: ")
        metadata_to_file_list.append("SUBTITLED: ")
        metadata_to_file_list.append("WATERMARKED: ")
        metadata_to_file_list.append(" ")
        metadata_to_file_list.append("EXTERNAL AUDIO SUMMARY: ")

    return metadata_to_file_list

def finishing_message(output_type, file_count, error_count):
    print("-"*60)
    print(f"Your {output_type}'s metadata has been written to ", end="")
    print(f"a text file to copy from here: {LOG_DIRECTORY}\n")

    if file_count == 0 and error_count == 0:
        pass
    else:
        print(f"Total files scanned for this {output_type}: {file_count}")
        print(f"Total error files for this {output_type}: {error_count}")


while True:
    choice = ""
    print('-'*60)
    print()
    global error_count
    global file_count
    error_count = 0
    file_count = 0

    while True:
        input_directory = input('Please drag in a file or folder to scan it: ')

        if illegal_apostrophe.search(input_directory):
            input_directory = input_directory.replace("'","")
        if illegal_quotes.search(input_directory):
            input_directory = input_directory.replace('"',"")
        if file_path_pattern.search(input_directory) or file_path_pattern_ending_backslash.search(input_directory):
            break
        else:
            print("Invalid file path, please try again.")
            continue

    root_length, folder_name_for_output_file = get_root_length(input_directory)
    os.chdir(LOG_DIRECTORY)
    global name_for_output_file
    
    # Determines whether to multiple file scan or single file scan
    if os.path.isdir(input_directory):
        while True:
            print("For the next prompt, please type 'y' or 'n' ")
            choice = input("Would you like to perform a deep scan? (y/n): ")
            choice = choice.lower()
            if choice == "y" or choice == "n":
                break
            else:
                continue

        print()
        output_type = "folder"
        complete_metadata_to_file_list = []
        # complete_deep_write_list = []

        name_for_output_file = get_file_name(input_directory)

        for root, folders, files in os.walk(input_directory):
            for file in files:
                if ghost_file_pattern.match(file):
                    continue
                current_root_split = root.split("\\")
                if choice == "n":
                    if len(current_root_split) > root_length:
                        continue
                
                name, ext = os.path.splitext(file)
                ext = ext.lower()
                if ext not in accepted_file_types:
                    continue
                
                file_path = os.path.join(root, file)
                metadata_to_file_list = get_file_metadata(file_path)
                print(ext)
                if ext == ".dng":
                    metadata_to_file_list.append(f"{ext} is not fully supported by PyMediaInfo: results may be inaccurate.")
                if ext == ".r3d":
                    metadata_to_file_list.append(f"{ext} is not supported by PyMediaInfo: results will be inexhaustive.")
                if "Error" in metadata_to_file_list:
                    error_count += 1
                else:
                    file_count += 1

                complete_metadata_to_file_list.append(metadata_to_file_list)
        
        if len(complete_metadata_to_file_list) == 0:
            print("The selection was empty. No files have been written!")
        else:
            write_log(complete_metadata_to_file_list)
            finishing_message(output_type, file_count, error_count)
    else:
        file = input_directory.split("\\")[-1]
        name, ext = os.path.splitext(file)
        error_count = 0
        file_count = 0
        output_type = "file"
        # complete_metadata_to_file_list is also here for a single file so that only one version of write_log() needs to exist.
        complete_metadata_to_file_list = []
        name_for_output_file = get_file_name(input_directory)
        metadata_to_file_list = get_file_metadata(input_directory)
        if ext == ".dng":
            metadata_to_file_list.append(f"{ext} is not fully supported by PyMediaInfo and so results may be inaccurate.")
        if ext == ".r3d":
            metadata_to_file_list.append(f"{ext} is not supported by PyMediaInfo: results will be inexhaustive.")
        if metadata_to_file_list == None:
            continue
        complete_metadata_to_file_list.append(metadata_to_file_list)
        if len(complete_metadata_to_file_list) == 0:
            print("The selection was empty. No files have been written!")
        else:
            write_log(complete_metadata_to_file_list)
            finishing_message(output_type, file_count, error_count)




# lEGACY BITS

# simplified_file_list.append("File_Name: " + file_name)
# simplified_file_list.append("File_Path: " + file_path)
# simplified_file_list.append("Date_Received: " + today)
# simplified_file_list.append("Texted_Subbed_Watermarked: ")
# simplified_file_list.append("File_Size: " + file_size_formatted)
# simplified_file_list.append("Duration: " + file_duration_formatted)

# deep_metadata_list.append("Colour Space: " + colour_space)
# simplified_file_list.append("Frame_Size: " + frame_size)
# simplified_file_list.append("Frame_Rate: " + frame_rate)
# simplified_file_list.append("Video_Codec: " + track.format)
# simplified_file_list.append("Bin_Location: ")

# deep_metadata_list.append("Audio Codec: " + str(audio_codec))
# deep_metadata_list.append("Audio Sample Rate: " + str(sample_rate))