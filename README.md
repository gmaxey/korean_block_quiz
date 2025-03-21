# Korean Block Quiz

A web-based quiz application to learn single-block Korean words, ranked by frequency of use. Built with Flask and containerized with Docker.

## Overview

This app helps learners memorize Korean Hangul blocks by matching them to their English translations. It uses a pre-generated `dictionary.tsv` file with frequency data to select words across 10 difficulty slices (most to least frequent). Features include:
- Interactive card-matching interface
- Frequency-based difficulty selection (1 = most frequent blocks, 10 = least frequent)
- Dynamic card replacement after 5 correct answers
- Hover-over full translations for long entries

## Prerequisites

- **Docker**: Install Docker on your system. See [Docker Installation Guide](https://docs.docker.com/get-docker/).
- **Internet Access**: Required to pull the image from Docker Hub or download dependencies during build.

## Option 1: Run Pre-Built Image from Docker Hub

The easiest way to run the app is to pull the pre-built image from Docker Hub.

 1. **Pull the Image**:
    ```bash
    docker pull gmaxey/korean_block_quiz:latest
    ```

 2. **Run the Container**:
    ```bash
    docker run -p 5000:5000 gmaxey/korean_block_quiz:latest
    ```
    - `-p 5000:5000`: Maps port 5000 on your host to the container’s port 5000.

 3. **Access the App**:
   - Open your browser to `http://localhost:5000`.
   - If on a remote server, use the server’s IP (e.g., `http://<server-ip>:5000`).

## Option 2: Build and Run from Source

If you want to build the image yourself (e.g., to modify code or data), follow
these steps:

 1. **Clone or Download the Repository**:
    - If hosted on GitHub, clone it:
      ```bash
      git clone <repository-url>

      cd korean-block-quiz
      ```
    - Otherwise, ensure you have all project files (`Dockerfile`, `app.py`,
      `templates/index.html`, `dictionary.tsv`, etc.) in a directory.

 2. **Run the Container**:
    ```bash
    docker build -t korean-block-quiz .

    `docker run -p 5000:5000 korean-block-quiz

    ```
    - This builds the image using the `Dockerfile`, installing dependencies and copying files.

 4. **Access the App**:
    - Open `http://localhost:5000` in your browser.
	
## Option 3: Run Locally with Python

To run the app locally without Docker (e.g., on Ubuntu for Windows 11 via WSL):

Ensure Python 3 is Installed:
`python3 --version`

If not, install:
```sudo apt update
sudo apt install python3 python3-pip```

Navigate to Project Directory:
`cd /path/to/korean-block-quiz`

Install Dependencies:
```pip3 install -r requirements.txt
pip3 install flask```

Run the App:
```export FLASK_APP=app.py
python3 -m flask run --host=0.0.0.0 --port=5000```
--host=0.0.0.0: Makes it accessible from your Windows browser.
--port=5000: Default port (change if needed).

Access the App:
Open http://localhost:5000 in your Windows browser.
If using WSL2 and localhost fails, find your WSL IP:
`ip addr show eth0 | grep inet`

Use the IP (e.g., http://172.18.x.x:5000).


## Usage

 - **Select Difficulty**: Use the "Frequency Slice" dropdown (1 = most frequent blocks, 10 = least frequent).
 - **Match Cards**: Click a Korean block and its English translation. Correct pairs gray out; incorrect pairs flash red.
 - **Reveal Answers**: Hold the "Reveal" button to see correct translations temporarily.
 - **Progress**: After 5 correct matches, the first 4 pairs are replaced with new ones. Complete 12 matches to finish a round.
 - **Restart**: Click "Restart" to start a new quiz with the selected slice.

## Troubleshooting

 - **Port Conflict**: If port 5000 is in use:
    1. Check running containers:
       ```bash
       docker ps
       ```
    2. Stop the conflicting container:
       ```bash
       docker stop <container_id>
       ```
  3. Retry running your container.

- **Image Pull Fails**: Ensure you’re logged into Docker Hub (`docker login`) if the repository becomes private, though it’s currently public.

- **Build Errors**: Verify all required files (e.g., `dictionary.tsv`) are present in the directory.

## Development Notes

- **Source Data**: The app uses `dictionary.tsv`, generated from Korean word frequency data (e.g., `kaikki.org-dictionary-Korean.jsonl`).
- **Dependencies**: See `requirements.txt` for Python packages (`flask`, `wordfreq`, `mecab-python3`), though only Flask is critical for the current version.
- **Customization**: Edit `app.py` or `templates/index.html` and rebuild to modify functionality or UI.

## Contributing

Feel free to fork, modify, and submit pull requests if hosted on a Git repository. For local changes, rebuild the image after edits.

## License

None

---

Built by Greg Maxey (and Grok 3) for learning Korean single-block words. Enjoy quizzing!

# Motivation and implementation

My prompt to Grok 3:

I'm trying to learn Korean and have been using Duolingo for the last 222 days. I find it very difficult to learn new words. I have a hypothesis that if I were to learn enough single-block words, it would make learning multi-block words easier, especially when the block have some relation to the work like with 신발, but even when they don't like with 양말, I have an extra set of mnemonic handles to grasp, as strange as sheep-horse might seem for "socks". I would to create a python-based web app to run on Ubuntu for Windows 11 to quiz me on single-block words. The words should be selected based on their frequency of use, both as word and as constituents of multi-block words.