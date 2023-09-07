# CGCookie Downloader

## Introduction

CGCookie Downloader is a tool designed to simplify the process of downloading courses from CGCookie. As someone who frequently travels and often finds themselves without internet access, I found it cumbersome to download courses one by one. This tool aims to streamline that process, allowing users to quickly and efficiently download entire courses for offline access.

**Disclaimer**: This tool is intended for personal use only. It's essential to respect the hard work of content creators. Please do not use this tool to exploit or distribute content without permission. Always support creators and platforms that provide quality content. CGCookie is one of the best in the industry, offering a vast array of high-quality courses and tutorials. If you find their content valuable, consider subscribing and supporting them.

## Features

- **Batch Download**: Download entire courses with a single command or click.
- **Django Web Interface**: A user-friendly web interface built with Django for easy interaction.
- **Terminal Version**: For those who prefer the command line, a terminal-based version is also available.
- **Automatic Login Detection**: The tool waits for you to log in and then proceeds with the download, ensuring a smooth experience.

## Installation & Usage

### Prerequisites

- Python 3.x
- pip
- Google Chrome

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/cgcookie-downloader.git
   cd cgcookie-downloader
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Using the Django Web Interface

1. Navigate to the project directory and run the Django server:
   ```bash
   python manage.py runserver
   ```

2. Open your browser and go to `http://127.0.0.1:8000/`.
3. Follow the on-screen instructions to download your desired course.

### Using the Terminal Version

1. Navigate to the project directory.
2. Run the script:
   ```bash
   python terminal_version.py
   ```

3. Follow the on-screen prompts to download your desired course.

## Contributing

If you'd like to contribute to this project, please fork the repository and submit a pull request. All contributions are welcome!

## License

This project is open-source and available under the MIT License. However, please ensure you use the tool responsibly and ethically.

## Acknowledgments

- Thanks to CGCookie for providing top-notch content and being an invaluable resource for learners worldwide.
- Thanks to the open-source community for the various libraries and tools that made this project possible.

---

This `README.md` provides a comprehensive overview of the project, its purpose, features, and usage instructions. You can customize it further based on any additional details or features you add to the project in the future.