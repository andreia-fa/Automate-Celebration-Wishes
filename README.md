# Automate Celebration Wishes

## Introduction

**Overview:**  
This project automates the process of sending celebration wishes and birthday messages to your contacts through Telegram.

## Further Reading

### Medium Article Series

If you want to follow a detailed, step-by-step guide about the Celebration Bot, check out the articles below:

- [Celebration’s Bot (Part I) – Setting up your GCP environment](https://medium.com/@andreia_fa/celebrations-bot-part-i-0cd809440e03) 

**Purpose:**  
The project aims to simplify and personalize the process of sending greetings by automating the message-sending process.

**Key Features:**
- Automatically sends celebration and birthday messages via Telegram.
- Supports customizable message templates.
- Logs successful message deliveries for tracking and auditing.

---

## Table of Contents

- [Project Title](#automate-celebration-wishes)
- [Introduction](#introduction)
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)
- [Configuration](#configuration)
- [Database Schema](#database-schema)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)
- [Support](#support)
- [FAQ](#faq)
- [Changelog](#changelog)

---

## Installation

### Prerequisites

Ensure you have the following installed on your system:
- Git
- Python 3.x

### Instructions

1. Clone the repository:

   git clone https://github.com/yourusername/automate-birthday-messages.git

  2. Install the required dependencies:
   
      *pip install -r requirements.txt*

  3. Adapt the configuration file as needed.
  4. Run the main file:

     *python main.py*
   

## Usage

1. **Initialize the database**  
   Run the DDL script to create the necessary tables.

2. **Insert contact data**  
   Insert contact rows manually or through the provided insert scripts.

3. **Start the automation**  
   Launch the main script:
   *python main.py*


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

## Telegram
 ```ini
telegram.api_id = your_telegram_api_id  
telegram.api_hash = your_telegram_api_hash  
telegram.session_file_name = your_telegram_session_file_name

```

## Database Setup

This project requires the following tables:
- `contacts_info`
- `contact_events`
- `messages`
- `message_log`

Here is the schema:

```sql
CREATE TABLE contacts_info (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    personal_relationship VARCHAR(255),
    message_receiver VARCHAR(255) NOT NULL,
    telegram_id VARCHAR(255),
    birthday_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE contact_events (
    id SERIAL PRIMARY KEY,
    contact_id INT REFERENCES contacts_info(id) ON DELETE CASCADE,
    event_type VARCHAR(50) NOT NULL,
    recurrence VARCHAR(50) NOT NULL,
    event_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE messages (
    id SERIAL PRIMARY KEY,
    text_message TEXT NOT NULL,
    type VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE message_log (
    id SERIAL PRIMARY KEY,
    contact_id INT REFERENCES contacts_info(id) ON DELETE CASCADE,
    message_id INT REFERENCES messages(id) ON DELETE SET NULL,
    sent_message TEXT NOT NULL,
    date_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) CHECK (status IN ('sent', 'failed', 'pending')) DEFAULT 'pending'
);

```

## Contributing

Contributing Guidelines:
Contributions are welcome! Please follow these steps:

1. Fork the Repository: Create a personal copy of the repository on GitHub.

2. Create a New Branch:
*git checkout -b feature-branch*

3. Make Your Changes: Implement your feature or fix the issue.
4. Commit your Changes:
*git commit -m 'Add some feature'*

5. Push to the Branch:
*git push origin feature-branch*

6. Open a Pull Request: Submit a pull request (PR) with a clear description of what was done.


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

**In Loving Memory of Mickey**

Every day with you was a celebration in itself.
Your love and warmth remain my guiding light.
You live on through me — in every act of kindness, in every celebration of life.

**Celebrating you always**

## Support
You can always reach me on telegram, under: @andreia_fa

## FAQ

Q: **Isn't this a bit sad, so you no longer message your special ones, in their celebrations?**

A: The goal ist to *guarantee* no matter what, that they recieve at least *one message*, 
ideally you should make their celebrations more special, how is up to you :) 

Q: **Can I create custom message templates?**

A: Yes! Add new entries to the messages table.

## Changelog
v1.0: Initial project setup.

v1.1: Added retry mechanism for message sending.
