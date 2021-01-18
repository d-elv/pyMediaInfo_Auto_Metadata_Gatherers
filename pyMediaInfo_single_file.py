from pymediainfo import MediaInfo
import datetime, time, re, os

output_dir = "\\\\10.10.52.250\\dropzone\\CTA\\09 SCRIPTS FOR CTA USE\\PyMediaInfo_single_files\\LOGGED_OUTPUT"

print("""Hello! Treat this program like MediaInfo, drag in files (literally click and drag), and then your chosen file's metadata will be written to a text file,
formatted to be sent on to Producers.

If you encounter any issues, please raise them to Dan and explain what happened.""")

print('-'*60)
print()
input_file = input('Please drag in a file to scan for metadata: ')

single_dig_pattern = re.compile(r'\.[0-9]')
illegal_apostrophe = re.compile(r"'")
illegal_quotes = re.compile(r'"')

if illegal_apostrophe.search(input_file):
    input_file = input_file.replace("'","")
if illegal_quotes.search(input_file):
    input_file = input_file.replace('"',"")

try:
    media_info = MediaInfo.parse(input_file)
except FileNotFoundError:
    print('Your file path is incorrect or your filename is missing the extension, please run the program again and try again.')


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
    
    file_duration_seconds = (file_duration_seconds / 1000)
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


writing_to_file_list = []
channel_layout_list = []
no_of_audio_channels = []
audio_track_counter = 0
print('Gathering metadata... ')

for track in media_info.tracks:
    if track.track_type == "General":
        
        # Gets file name on its own
        file_name = track.complete_name
        file_name = file_name.replace('\\', '/')
        file_name = file_name.split('/')
        file_name = file_name[-1]
        file_path = track.complete_name

        file_name_for_output_file = file_name[:-4]

        file_duration_seconds = track.duration
        file_duration_formatted = timeFormatter(file_duration_seconds)
        file_size_formatted = fileSizeFormatter(track.file_size)
        
        

        writing_to_file_list.append("File Name: " + file_name)
        writing_to_file_list.append("File Size: " + file_size_formatted)
        writing_to_file_list.append("File Path: " + file_path)
        writing_to_file_list.append("Duration: " + file_duration_formatted)

    elif track.track_type == "Video":
        
        aspect_ratio = track.display_aspect_ratio
        # THIS NEEDS TO BE CHECKED AGAINST ALL DIFFERENT ASPECT RATIOS | POTENTIALLY TURN INTO ITS OWN HELPER FUNCTION
        if aspect_ratio == "1.778":
            aspect_ratio = "16x9"
        elif aspect_ratio == "1.000":
            aspect_ratio = "1x1"
        elif aspect_ratio == "1.875":
            aspect_ratio = "Letterboxed 16x9"
        elif aspect_ratio == "0.800":
            aspect_ratio = "4x5"
        elif aspect_ratio == "0.563":
            aspect_ratio = "9x16"

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
        writing_to_file_list.append("Bit Rate: " + bit_rate)
   
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


writing_to_file_list.append('No. of Audio Channels: ' + str(audio_track_counter))
writing_to_file_list.append("No. of Audio Tracks per Channel, in order: " + str(no_of_audio_channels)[1:-1])

if len(channel_layout_list) > 0 and None not in channel_layout_list:
    writing_to_file_list.append("Track Layout: " + str(channel_layout_list))

print('-'*60)

os.chdir(output_dir)
with open(file_name_for_output_file + "_MediaInfo_Output.txt", "w" ) as log_file:
        
    for attribute in writing_to_file_list:
        log_file.write(str(attribute))
        log_file.write("\n")

print("Your file's metadata has been written to a text file to copy from here: " + str(output_dir) + "\n")
time.sleep(10)
