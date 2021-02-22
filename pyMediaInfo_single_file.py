from pymediainfo import MediaInfo
import datetime 
import time 
import re 
import os

LOG_DIRECTORY = "\\\\10.10.52.250\\dropzone\\CTA\\08 PYTHON PROGRAMS\\02_PYMEDIAINFO\\01_Single_File\\LOGGED OUTPUT"

print("""Hello! Treat this program like MediaInfo, drag in files (literally 
click and drag), and then your chosen file's metadata will be written to a 
text file, formatted to be sent on to Producers.

This program will loop endlessly, simply close it once you're finished.

If you encounter any issues, raise them to Dan and explain what happened.""")

single_dig_pattern = re.compile(r'\.[0-9]')
illegal_apostrophe = re.compile(r"'")
illegal_quotes = re.compile(r'"')


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
    
    file_duration_seconds = (file_duration_seconds / 1000)
    file_duration_seconds = int(file_duration_seconds)
    file_duration_formatted = str(datetime.timedelta(seconds=file_duration_seconds))
    file_duration_formatted = str(file_duration_formatted) + file_duration_milli
    
    return file_duration_formatted


def format_bit_rate(bit_rate_raw):
    if bit_rate_raw < (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / 1000
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-1] + " KB/s"
    if bit_rate_raw > (1000 * 1000):
        bit_rate_formatted = bit_rate_raw / (1000 * 1000)
        bit_rate_formatted = str(bit_rate_formatted)
        bit_rate_formatted = bit_rate_formatted[:-2] + " MB/s"
    
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
    return formatted_aspect_ratio


def get_file_name(input_file):
    name = input_file
    name = name.replace("\\", "/")
    name = name.split("/")
    name = name[-1]
    return name

while True:

    print("-"*60)
    print()
    input_file = input("Please drag in a file to scan for metadata: ")
    name = get_file_name(input_file)
    print(f"Gathering metadata of... {name} ")

    if illegal_apostrophe.search(input_file):
        input_file = input_file.replace("'","")
    if illegal_quotes.search(input_file):
        input_file = input_file.replace('"',"")

    try:
        media_info = MediaInfo.parse(input_file)
    except FileNotFoundError:
        print("Your file path is incorrect or your filename ", end="")
        print("is missing its extension, please try again.")
        continue

    writing_to_file_list = []
    simplified_file_list = []
    channel_layout_list = []
    no_of_audio_channels = []
    audio_track_counter = 0

    for track in media_info.tracks:
        if track.track_type == "General":
            
            # Gets file name on its own
            file_name = get_file_name(track.complete_name)
            file_path = track.complete_name

            file_name_for_output_file = file_name[:-4]

            file_size_raw = track.file_size
            if track.file_size == 0 or track.file_size == None:
                print(f"{file_name} is a corrupt file, please ", end="")
                print(f"investigate, resupply and try scanning again.")
                break
            else:
                pass


            file_duration_seconds = track.duration
            file_duration_formatted = format_milliseconds(file_duration_seconds)
            file_size_formatted = format_file_size(file_size_raw)

            writing_to_file_list.append("File Name: " + file_name)
            writing_to_file_list.append("File Size: " + file_size_formatted)
            writing_to_file_list.append("File Path: " + file_path)
            writing_to_file_list.append("Duration: " + file_duration_formatted)
            
            today = get_date()
            simplified_file_list.append("File_Name: " + file_name)
            simplified_file_list.append("File_Path: " + file_path)
            simplified_file_list.append("Date_Received: " + today)
            simplified_file_list.append("Texted_Subbed_Watermarked: ")
            simplified_file_list.append("File_Size: " + file_size_formatted)
            simplified_file_list.append("Duration: " + file_duration_formatted)



        elif track.track_type == "Video":
            
            aspect_ratio = format_aspect_ratio(track.display_aspect_ratio)

            video_width = track.width
            video_height = track.height
            frame_size = str(video_width) + "x" + str(video_height)
            colour_space = str(track.color_space) + " " + str(track.color_primaries)

            try:
                bit_rate = format_bit_rate(track.bit_rate)
            except:
                bit_rate = "Could not acquire"

            if track.frame_rate == None:
                frame_rate = track.original_frame_rate
            else:
                frame_rate = track.frame_rate

            if track.format_profile == None:
                format_profile = track.codec_id
            else:
                format_profile = track.format_profile

            writing_to_file_list.append("Frame Size: " + frame_size)
            writing_to_file_list.append("Aspect Ratio: " + aspect_ratio)
            writing_to_file_list.append("Frame Rate: " + frame_rate)
            writing_to_file_list.append("Video Codec: " + track.format)
            writing_to_file_list.append("Video Format Profile: " + format_profile)
            writing_to_file_list.append("Colour Space: " + colour_space)
            writing_to_file_list.append("Bit Rate: " + bit_rate)

            simplified_file_list.append("Frame_Size: " + frame_size)
            simplified_file_list.append("Frame_Rate: " + frame_rate)
            simplified_file_list.append("Video_Codec: " + track.format)
            simplified_file_list.append("Bin_Location: ")
    
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
        writing_to_file_list.append("Track Layout: " + str(channel_layout_list)[2:-2])

    print("-"*60)

    def write_log():
        os.chdir(LOG_DIRECTORY)
        with open(file_name_for_output_file + "_MediaInfo_Output.txt", "w" ) as log_file:
                
            for attribute in writing_to_file_list:
                log_file.write(str(attribute))
                log_file.write("\n")

            log_file.write("\n"*2)
            log_file.write("SIMPLIFIED - COPY THIS TO CLICKUP\n")

            for attribute in simplified_file_list:
                log_file.write(str(attribute))
                log_file.write("\n")

        print("Your file's metadata has been written to a text file to ", end="")
        print(f"copy from here: {LOG_DIRECTORY}\n")
    
    if file_size_raw == 0 or file_size_raw == None:
        pass
    else:
        write_log()
