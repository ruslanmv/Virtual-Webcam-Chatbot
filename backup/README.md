# Creating a Virtual Webcam Chatbot That Responds to Voice Commands in a Video Meeting

## Introduction

In this tutorial, we'll walk you through the process of creating a virtual webcam chatbot that responds to voice commands in a video meeting. The chatbot will listen for a specific activation word, transcribe audio from the  microphone or Virtual Audio, send the text to the ChatGPT API, and display the chatbot's response on the virtual webcam video feed.

Requirements:

- Python 3.10 or higher
- OpenCV
- PyVirtualCam
- SpeechRecognition
- Requests

##  Step 1:  Environment Setup
 
First we are going to install our enviroment with python 3.10.11 here , after you installed in your working directory you can create your enviroment

```
python -m venv .venv

```

You’ll notice a new directory in your current working directory with the same name as your virtual environment, then activate the virtual environment.


```
.venv\Scripts\activate.bat

```

usually is convinent having the latest pip

python -m pip install --upgrade pip

then we install our notebook, because also you can use Jupyter Notebook


```
pip install ipykernel notebook

```


```
python -m ipykernel install --user --name watson --display-name "Python (watson)"

```


Before we begin, let's make sure we have all the necessary libraries installed. Open your command prompt or terminal and run the following command:

```bash
pip install opencv-python-headless numpy pyvirtualcam SpeechRecognition requests python-dotenv
```

## Step 2 : API keys 

To get an API key from OpenAI, you'll need to sign up for an account and access the API key from the OpenAI Dashboard. Here's a step-by-step guide:
1. Go to the OpenAI website: https://www.openai.com/
2. Click on the "Get started" or "Sign up" button to create a new account. If you already have an account, click on "Log in" to sign in to your account.
3. After signing up or logging in, you'll be redirected to the OpenAI Dashboard.
4. On the Dashboard, click on the "API Keys" tab in the sidebar menu.
5. You should see a list of your API keys. If you don't have any API keys, click on the "Create API Key" button.
6. Fill in the required information for the new API key, such as a name and a description. Select the appropriate permissions for the key, then click "Create".
7. Once the API key is created, you'll see the key in the API Keys list. Copy the API key to use it in your application. Remember to keep the key secure, as it provides access to the OpenAI API with your account's permissions.
8. To add an API key in a .env file for the given code, first, create a .env file in your project directory and add the API key like this:

```
CHATGPT_API_KEY=your_api_key_here
```

9. Then we create a file  `watson.py` where we are going to add our pieces of code.
## Step 2: Set Up Virtual Audio Cable (Optional)
If you want to use Virtual Audio Cable to capture audio, follow these steps:

1. Download and install Virtual Audio Cable software like VB-CABLE (compatible with Windows).

2. Set Virtual Audio Cable as the default recording device in your system's sound settings.

If we are going to use this audio cable we should  adjust the device index in the code (in the `listen_and_transcribe` function) to match the Virtual Audio Cable device. By default, it is set to `1`. 

## Step 3: Define the ChatGPT API Function

The first we create a Python function that sends a request to the ChatGPT API and receives a response. This function will allow our chatbot to generate responses based on the given text. Here's the code:

```python
import requests
from dotenv import load_dotenv
load_dotenv()

def chatbot_response(text):

    api_key = os.getenv('CHATGPT_API_KEY')
    api_url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": f"Chatbot says: {text}",
        "max_tokens": 50,
        "n": 1,
        "stop": None,
        "temperature": 1
    }
    response = requests.post(api_url, json=data, headers=headers)
    response_json = response.json()
    if 'choices' in response_json:
        return response_json['choices'][0]['text'].strip()
    else:
        return "Error getting chatbot response"
```

## Step 4: Create a Function to Transcribe Audio

We need a function that captures audio from the microphone or Virtual Audio Cable and converts it into text using the SpeechRecognition library. This will allow our chatbot to understand voice commands. Here's the code:

```python
import speech_recognition as sr

def listen_and_transcribe(source_type="microphone"):
    recognizer = sr.Recognizer()

    if source_type == "microphone":
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
    elif source_type == "virtual_audio_cable":
        with sr.Microphone(device_index=1) as source:  # Adjust device_index based on your system configuration
            print("Listening...")
            audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"Transcribed: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return None
```

## Step 5: Set Up the Virtual Webcam

To display the chatbot's responses, we'll create a virtual webcam using the PyVirtualCam library. This will allow us to stream a video feed with the chatbot's text overlay. Add the following code:

```python
import cv2
import numpy as np
import pyvirtualcam

# Set up the virtual webcam
width, height, fps = 640, 480, 30
blank_image = np.zeros((height, width, 3), np.uint8)
```

## Step 6: Combine the Components in the Main Loop

Now, let's combine all the components in the main loop. This loop will continuously capture audio, transcribe it, send the text to the ChatGPT API, and display the chatbot's response on the virtual webcam video feed. Here's the complete code:

```python
# Start the virtual webcam
with pyvirtualcam.Camera(width, height, fps) as cam:
    while True:
        # Capture audio from the microphone or Virtual Audio Cable, transcribe it
        input_text = listen_and_transcribe(source_type="virtual_audio_cable")  # Change to "microphone" if not using Virtual Audio Cable

        if input_text is not None and "computer" in input_text.lower():
            # Remove the word "computer" from the transcribed text
            input_text = input_text.lower().replace("computer", "").strip()

            # Send the text to the ChatGPT API and get a response
            response = chatbot_response(input_text)
        else:
            response = "Waiting for the activation word..."

        # Create a new frame with the chatbot's response text
        frame = blank_image.copy()
        cv2.putText(frame, response, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Send the frame to the virtual webcam
        cam.send(frame)

        # Wait for the next frame
        cam.sleep_until_next_frame()
```

## Full code of the program:

```python
import cv2
import numpy as np
import pyvirtualcam
import speech_recognition as sr
import requests
from dotenv import load_dotenv
load_dotenv()
# Set up the virtual webcam
width, height, fps = 640, 480, 30
blank_image = np.zeros((height, width, 3), np.uint8)

# Define the ChatGPT API function
def chatbot_response(text):
    api_key = os.getenv('CHATGPT_API_KEY')
    api_url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": f"Chatbot says: {text}",
        "max_tokens": 50,
        "n": 1,
        "stop": None,
        "temperature": 1
    }
    response = requests.post(api_url, json=data, headers=headers)
    response_json = response.json()
    if 'choices' in response_json:
        return response_json['choices'][0]['text'].strip()
    else:
        return "Error getting chatbot response"

# Create a function to transcribe audio
def listen_and_transcribe(source_type="microphone"):
    recognizer = sr.Recognizer()

    if source_type == "microphone":
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)
    elif source_type == "virtual_audio_cable":
        with sr.Microphone(device_index=1) as source:  # Adjust device_index based on your system configuration
            print("Listening...")
            audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print(f"Transcribed: {text}")
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
    return None

# Start the virtual webcam
with pyvirtualcam.Camera(width, height, fps) as cam:
    while True:
        # Capture audio from the microphone or Virtual Audio Cable, transcribe it
        input_text = listen_and_transcribe(source_type="virtual_audio_cable")

        if input_text is not None and "computer" in input_text.lower():
            # Remove the word "computer" from the transcribed text
            input_text = input_text.lower().replace("computer", "").strip()

            # Send the text to the ChatGPT API and get a response
            response = chatbot_response(input_text)
        else:
            response = "Waiting for the activation word..."

        # Create a new frame with the chatbot's response text
        frame = blank_image.copy()
        cv2.putText(frame, response, (50, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        # Send the frame to the virtual webcam
        cam.send(frame)

        # Wait for the next frame
        cam.sleep_until_next_frame()


```

## Step 7 How to run this program

To run the program during your meeting, follow these steps:

1. Open your command prompt or terminal.
2. Navigate to the directory where  will  saved the Python script `watson.py`.
3. Run the following command to start the program:

```bash
python watson.py
```

4. Once the program starts, make sure your microphone or Virtual Audio Cable is properly configured and set as the default recording device.

5. Speak the activation word ("computer" by default) followed by your voice command in the meeting.

6. The chatbot will transcribe your voice command, send it to the ChatGPT API, and display the chatbot's response on the virtual webcam video feed.

Remember to replace `"your_api_key"` with your actual ChatGPT API key before running the code in the .env file. Additionally, modify the `source_type` argument in the `listen_and_transcribe` function call to `"virtual_audio_cable"` if using Virtual Audio Cable or `"microphone"` for the default microphone.

Enjoy experimenting with your virtual webcam chatbot during your meetings!

## Conclusion:

Congratulations! You have successfully created a virtual webcam chatbot that responds to voice commands in a video meeting. The chatbot listens for the activation word, transcribes the audio using the microphone or Virtual Audio Cable (based on your choice), sends the text to the ChatGPT API, and displays the chatbot's response on the virtual webcam video feed.

Enjoy experimenting with your virtual webcam chatbot!


audio/ogg format

Ogg (audio/ogg) is an open container format that is maintained by the Xiph.org Foundation (xiph.org/ogg). You can use audio streams that are compressed with the following lossy codecs:

Opus (audio/ogg;codecs=opus). For more information, see opus-codec.org and Opus (audio format). Look especially at the Containers section.
Vorbis (audio/ogg;codecs=vorbis). For more information, see xiph.org/vorbis and Vorbis.
OGG Opus is the preferred codec. It is the logical successor to OGG Vorbis because of its low latency, high audio quality, and reduced size. It is standardized by the Internet Engineering Task Force (IETF) as Request for Comment (RFC) 6716.

If you omit the codec from the content type, the service automatically detects it from the input audio.