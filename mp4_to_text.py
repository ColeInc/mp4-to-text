import os
from dotenv import load_dotenv
import moviepy.editor as mp
import speech_recognition as sr
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def get_filenames_from_directory():
    print("fetching mp4 videos in input dir...")
    filenames = []
    # Check if the directory exists
    if os.path.exists("IN"):
        # Iterate over all files in the specified directory
        for filename in os.listdir("IN"):
            # Check if the file has a .mp4 extension
            if filename.endswith(".mp4"):
                filenames.append(filename)
    else:
        print("Could not find IN directory.")
        
    print("mp4 filenames FOUND:", filenames)
    return filenames


def get_full_filename(filename):
    # print("getting full filename...")
    # # Split the filename into its root and extension parts
    # root, extension = os.path.splitext(filename)

    # # Check if there are multiple dots in the filename
    # if extension and "." in root:
    #     # Split the root part using the last dot
    #     root_parts = root.split(".")
    #     root = ".".join(root_parts[:-1])

    # # Combine the root and extension to get the full filename
    # full_filename = root + extension
    # print("full_filename:", full_filename)
    # return full_filename
    
    # Split the filename based on the last dot (.).
  split_filename = filename.rsplit('.', 1)

  # If there's no dot (no extension), return the entire filename.
  if len(split_filename) == 1:
    return filename
  # Otherwise, return the part before the last dot (the filename).
  else:
    return split_filename[0]


def extract_audio_from_video(file_name):
    print("extracting audio from mp4 file...")

    # Define the output directory name
    staging_directory = "STAGING"
    # Create the staging directory if it doesn't exist
    if not os.path.exists(staging_directory):
        os.makedirs(staging_directory)

        # Load the video
    print("loading video file...")
    video = mp.VideoFileClip(os.path.join("IN", file_name + ".mp4"))

    # Construct the output file path in the staging directory
    output_file_name = os.path.join(staging_directory, file_name + ".wav")

    # Extract the audio from the video
    print("Extracting audio from the video...")
    audio_file = video.audio
    audio_file.write_audiofile(output_file_name)

    print(f"Audio extracted and saved to '{output_file_name}'")


def extract_text_from_audio(file_name):
    print("extracting text from audio file...")
    staging_directory = "STAGING"

    # Initialize recognizer
    print("Initializing the speech recognizer...")
    r = sr.Recognizer()

    audio_file_name = os.path.join(staging_directory, file_name + ".wav")

    # Load the audio file
    print("Loading the audio file...")
    with sr.AudioFile(audio_file_name) as source:
        data = r.record(source)

    # Convert speech to text
    print("Converting speech to text... (this part takes the longest)")
    text = r.recognize_google(data)

    # Print the text
    # print("\nFinal text from the video is:\n")
    # print(text)
    print("Successfully converted to text!")
    return text


def execute_gemini_prompt(transcript_text):
    print("Sending prompt to Gemini AI...")
    
    model = genai.GenerativeModel("gemini-pro")

    prompt = "Please format the following text with the correct syntax, paragraphs, commas, and periods. Please don't change the order of the words at all though. keep them how they are."

    response = model.generate_content(f"{prompt}\n\n{transcript_text}")
    print("//////////////////////////")
    print("RESPONSE:\n", response.text)
    print("//////////////////////////")
    return response.text


def write_text_to_file(file_name, text):
    print("Writing text to output file...")

    # Define the directory name
    out_directory = "OUT"
    # Create the OUT directory if it doesn't exist
    if not os.path.exists(out_directory):
        os.makedirs(out_directory)

    # Construct the output file path
    output_file_path = os.path.join(out_directory, file_name + ".txt")

    # Check if the file already exists
    file_exists = os.path.exists(output_file_path)

    # If the file exists, append "_2" to the file name
    if file_exists:
        output_file_path = os.path.join(out_directory, file_name + "_2.txt")

    # Write the text to the output file
    with open(output_file_path, "w") as file:
        file.write(text)

    print(f"Successfully wrote text to '{output_file_path}'")


def delete_files_by_basename(filename):
    print("deleting the files from the IN and STAGING directories...")
    directories = ["IN", "STAGING"]
    deleted_files = []
    for directory in directories:
        directory_path = os.path.join(os.getcwd(), directory)
        if os.path.exists(directory_path):
            for file_name in os.listdir(directory_path):
                if os.path.splitext(file_name)[0] == filename:
                    file_path = os.path.join(directory_path, file_name)
                    os.remove(file_path)
                    deleted_files.append(file_name)
    if len(deleted_files) > 0:
        print("Deleted files:", deleted_files)
    else:
        print("No files matching the basename were found.")
    return deleted_files


def main():
    print("Starting...")
    
    # fetch all mp4 files from the IN directory
    video_filenames = get_filenames_from_directory()
    for video in video_filenames:
        # get file's basename
        file_name = get_full_filename(video)
        print("filename:", file_name)
        # extracts the audio from the video file
        extract_audio_from_video(file_name)
        # uses the extracted audio to generate text (presumably through some form of speech-to-text)
        extracted_text = extract_text_from_audio(file_name)
        # formats the extracted text according to the Gemini prompt (the specifics of this would depend on what the Gemini prompt is)
        formatted_text = execute_gemini_prompt(extracted_text)
        # writes the formatted text to a file
        write_text_to_file(file_name, formatted_text)
        # once successfully written, delete mp4 files from IN and STAGING dirs:
        delete_files_by_basename(file_name)
        # delete_files_by_basename("test copy")
    print("Complete! ✅")
    
main()