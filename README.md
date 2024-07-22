# Automate Celebration Wishes

## Introduction
- **Overview:** This project automates the process of sending celebration wishes and birthday messages to your contacts.
- **Purpose:** The project aims to simplify the process of sending personalized greetings by automating the task of sending *celebration/birthday* messages.
- **Key Features:** 
  - Automatically sends celebration/birthday messages via Telegram text message.
  - Users can create and customize their own message templates.
  - Notification of successful message delivery.

## Table of Contents
1. [Project Title](#project-title)
2. [Introduction](#introduction)
3. [Table of Contents](#table-of-contents)
4. [Installation](#installation)
5. [Usage](#usage)
6. [Features](#features)
7. [Configuration](#configuration)
8. [Contributing](#contributing)
9. [License](#license)
10. [Credits](#credits)
11. [Support](#support)
12. [FAQ](#faq)
13. [Changelog](#changelog)

## Installation
- **Prerequisites:** Ensure you have Git and Python installed on your system.
- **Instructions:**
  1. Clone the repository:
     ```bash
     git clone https://github.com/yourusername/automate-birthday-messages.git
     ```
  2. Install the required dependencies:
     ```bash
     pip install -r requirements.txt
     ```
  3. Adapt the configuration file as needed.
  4. Run the main file:
     ```bash
     python main.py
     ```

## Usage
(Provide detailed instructions, example commands, and expected outputs here. Include screenshots if applicable.)

## Features
- Automatically sends celebration/birthday messages via Telegram text message.
- Users can create and customize their own message templates.
- Notification of successful message delivery.

## Configuration
Users can customize the following parameters in the configuration file:

- **Database Configuration:**
  ```ini
  database.url = your_database_host
  database.port = your_database_port
  database.username = your_database_username
  database.password = your_database_password
  database.db_name = your_database_name
  database.contacts_table = contacts_info
  database.messages_table = messages

**Telegram API**
 ```ini
telegram.api_id = your_telegram_api_id
telegram.api_hash = your_telegram_api_hash
telegram.session_file_name = your_telegram_session_file_name

**SQL Table Definitions**

**contact info table**

```ini

CREATE TABLE `contacts_info` (
  `Username` varchar(255) DEFAULT NULL,
  `Personal_relationship` varchar(255) DEFAULT NULL,
  `Message_receiver` varchar(255) DEFAULT NULL,
  `Telegram_name` varchar(255) DEFAULT NULL,
  `Birthday_date` date DEFAULT NULL,
  `Created_at` date DEFAULT NULL,
  `Updated_at` date DEFAULT NULL,
  `Recurrence` varchar(255) DEFAULT NULL,
  `Type` varchar(255) DEFAULT NULL
);

**message table**
CREATE TABLE `messages` (
  `id` int NOT NULL AUTO_INCREMENT,
  `text_message` text,
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`)
);


## Contributing

Contributing Guidelines:
Contributions are welcome! Please follow these steps:

1. Fork the Repository: Create a personal copy of the repository on GitHub.

2. Create a New Branch:
git checkout -b feature-branch

3. Make Your Changes: Implement your feature or fix the issue.
4. Commit your Changes:
git commit -m 'Add some feature'

5.Push to the Branch:
git push origin feature-branch

6.Open a Pull Request: Submit a pull request (PR) with a clear description of what was done.

```

## Code of Conduct:
All contributions are expected to respect others and to promote inclusivity and collaboration.

## Code Style:

Follow the existing coding style in the project (if applicable).
Use clear and descriptive names for variables, functions, and classes.
Testing:

Ensure your changes are tested. If the project includes tests, run them to make sure nothing is broken.
If adding new features, include tests that cover the new functionality.
Documentation:

Update the documentation to reflect any changes or new features.
Make sure to provide clear and concise descriptions in your code comments.

## License
This project is licensed under the MIT License. See the LICENSE file for details.

## Credits
(Provide acknowledgments and references here.)

## Support
(Provide support contact information or resources here.)

## FAQ
(Add frequently asked questions and answers here.)

## Changelog
(Add details of changes and updates here.)
