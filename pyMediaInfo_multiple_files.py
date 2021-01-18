from pymediainfo import MediaInfo
import time, re, datetime, os

output_dir = "\\\\10.10.52.250\\dropzone\\CTA\\09 SCRIPTS FOR CTA USE\\pyMediaInfo_multiple_files\\LOGGED OUTPUT"
txt_file_underscores = "_"*50

print("""Hello! Treat this program like MediaInfo, but for folders! Drag in the folder you want to scan the media files inside of (literally click and drag), and then each file's metadata
will be written to a text file, ready to be copied from and sent on to Producers.
e
If you encounter any issues, please raise them to Dan and explain what happened.""")

print('-'*60)
print()
input_dir = input('Please drag in a folder to scan its files: ')

single_dig_pattern = re.compile(r'\.[0-9]')
illegal_apostrophe = re.compile(r"'")
illegal_quotes = re.compile(r'"')

if illegal_apostrophe.search(input_dir):
    input_dir = input_dir.replace("'","")
if illegal_quotes.search(input_dir):
    input_dir = input_dir.replace('"',"")

ghost_file_pattern = re.compile(r'^(\.)[<>-_.,+!?£$%^&*a-zA-Z0-9]*')
accepted_file_types = ['.mov', '.mxf', '.avi', '.wav', '.mp3', '.mp4', '.jpg', '.tif', '.tiff', '.aif', '.aiff', \
    '.png', '.jpeg', '.tiff', '.wmv', '.mkv',]

def fileSizeFormatter(file_size):
    # formats file sizes from bytes so that they are easily readable
    if file_size > 1000000000:
        file_size = file_size / 1000000000
        file_size = str(file_size)
        file_size = file_size[:7] + "GB"
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


def timeFormatter(file_duration_seconds):
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
    
    return file_duration_formatted

def formatBitRate(bit_rate_raw):
    if bit_rate_raw < (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / 1000
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-4] + " KB/s"
    if bit_rate_raw > (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / (1000 * 1000)
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-4] + " MB/s"
    
    return bit_rate_formatted

def aspectRatioFormatter(aspect_ratio_raw):
    if aspect_ratio_raw == "1.778":
        aspect_ratio_raw = "16x9"
    elif aspect_ratio_raw == "1.000":
        aspect_ratio_raw = "1x1"
    elif aspect_ratio_raw == "1.875":
        aspect_ratio_raw = "Letterboxed 16:9"
    elif aspect_ratio_raw == "0.800":
        aspect_ratio_raw = "4x5"
    elif aspect_ratio_raw == "0.563":
        aspect_ratio_raw = "9x16"
    elif aspect_ratio_raw == "1.896":
        aspect_ratio_raw = "2x1"
    return aspect_ratio_raw

def rootLengthGetter():
    # Gets the root length of the directory given for scanning,
    # This is later used to ensure no sub folders are scanned.
    for root, dir_path, files in os.walk(input_dir):
        root_splitter = root.split("\\")
        folder_name_for_output_file = root_splitter[-1]
        root_length = len(root_splitter)
        return root_length, folder_name_for_output_file


for root, dir_path, files in os.walk(input_dir):
    for file in files:
        
        file_name, ext = os.path.splitext(file)
        ext = ext.lower()
        if ext not in accepted_file_types:
            continue

        writing_to_file_list = []
        channel_layout_list = []
        no_of_audio_channels = []
        audio_track_counter = 0
        
        current_root_split = root.split("\\")
        root_length, folder_name_for_output_file = rootLengthGetter()
        if len(current_root_split) > root_length:
            continue
        if ghost_file_pattern.match(file):
            continue

        file_path = os.path.join(root, file)

        print("Gathering metadata for... " + file)
        try:
            file_media_info = MediaInfo.parse(file_path)
        except FileNotFoundError:
            print("Your file path is incorrect or your filename is missing to extension, \
                please run the program and try again.")
            time.sleep(5)
        
        for track in file_media_info.tracks:
            if track.track_type == "General":

                file_name = track.complete_name
                file_name = file_name.replace('\\', '/')
                file_name = file_name.split('/')
                file_name = file_name[-1]
                current_file_path = track.complete_name

                file_duration_seconds = track.duration
                file_duration_formatted = timeFormatter(file_duration_seconds)
                file_size_formatted = fileSizeFormatter(track.file_size)

                writing_to_file_list.append("File Name: " + file_name) 
                writing_to_file_list.append("File Size: " + file_size_formatted)
                writing_to_file_list.append("File Path: " + current_file_path)
                writing_to_file_list.append("Duration: " + file_duration_formatted)

            elif track.track_type == "Video":
                
                aspect_ratio = aspectRatioFormatter(track.display_aspect_ratio)

                video_width = track.width
                video_height = track.height
                frame_size = str(video_width) + 'x' + str(video_height)
                colour_space = str(track.color_space) + ' ' + str(track.color_primaries)
                bit_rate = formatBitRate(track.bit_rate)
                writing_to_file_list.append("Frame Size: " + frame_size)
                writing_to_file_list.append("Aspect Ratio: " + aspect_ratio)
                writing_to_file_list.append("Frame Rate: " + track.frame_rate)
                writing_to_file_list.append("Video Codec: " + track.format)
                writing_to_file_list.append("Video Format Profile: " + track.format_profile)
                writing_to_file_list.append("Colour Space: " + colour_space)
                writing_to_file_list.append("Bit Rate: " + str(bit_rate))

            elif track.track_type == "Audio":
                audio_codec = track.format
                sample_rate = track.sampling_rate
                channel_layout = track.channel_layout
                no_of_audio_channels.append(track.channel_s)
                channel_layout_list.append(channel_layout)

                audio_track_counter += 1
                if audio_track_counter > 1:
                    continue

                writing_to_file_list.append("Audio Codec: " + str(audio_codec))
                writing_to_file_list.append("Audio Sample Rate: " + str(sample_rate))
        
        writing_to_file_list.append("No. of Audio Channels: " + str(audio_track_counter))
        writing_to_file_list.append("No. of Audio Tracks per Channel, in order: " + str(no_of_audio_channels)[1:-1])

        if len(channel_layout_list) > 0 and None not in channel_layout_list:
            writing_to_file_list.append("Track Layout: " + str(channel_layout_list))

        os.chdir(output_dir)
        with open(folder_name_for_output_file + "_MediaInfo_Output.txt", "a") as log_file:

            for attribute in writing_to_file_list:
                log_file.write(str(attribute))
                log_file.write("\n")

            log_file.write(txt_file_underscores)
            log_file.write("\n"*2)
        
print("Your folder's metadata has been written to a text file to copy from here: " + str(output_dir) + "\n")
time.sleep(10)
