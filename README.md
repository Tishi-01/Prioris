# Prioris — Task Manager

An Eisenhower Matrix-based task manager built with Python & Tkinter, featuring WiFi-aware and weather-aware smart task suggestions.

## Features

- **Eisenhower Matrix** — Organize tasks into 4 priority quadrants
- **Smart Suggestions** — Tasks auto-suggested based on your WiFi network and local weather (rain prediction)
- **Tag System** — WiFi-linked and Weather-linked tags for context-aware task surfacing
- **Filters** — View All, Today, or Completed tasks
- **Animated UI** — Smooth checkbox and tick animations
- **Google Maps Integration** — Pick city on a map for weather-based tags

## Tech Stack

- **UI**: Tkinter + Pillow
- **Database**: MySQL
- **Weather API**: OpenWeatherMap
- **City Picker**: Flask + Google Maps API

## Project Structure

```
prioris/
├── main.py                    # Entry point
├── config.py                  # Configuration & constants
├── database/
│   ├── connection.py          # MySQL connection
│   └── queries.py             # All DB operations
├── services/
│   ├── wifi.py                # WiFi IP detection
│   ├── weather.py             # Rain prediction
│   └── city_picker.py         # Google Maps city picker
├── ui/
│   ├── app.py                 # Main application class
│   ├── utils.py               # Rounded rects, animations
│   ├── sidebar.py             # Suggested tasks sidebar
│   ├── filters.py             # Filter buttons
│   ├── matrix.py              # Eisenhower matrix
│   └── popups/
│       ├── add_task.py        # Add task form
│       ├── tag_manager.py     # View/delete tags
│       └── edit_tag.py        # Add/edit tags
└── assets/                    # Logo & assets
```

## Setup

1. Install dependencies:
   ```bash
   pip install mysql-connector-python Pillow flask requests
   ```

2. Set up MySQL database `prioris` with tables `taskinfo` and `tags`.

3. Update `config.py` with your database credentials and API keys.

4. Run:
   ```bash
   python main.py
   ```

## Database Schema

### `taskinfo`
| Column     | Type         |
|------------|-------------|
| taskName   | VARCHAR      |
| Category   | INT (1-4)    |
| Tag        | VARCHAR      |
| taskStatus | INT (0/1)    |
| deadline   | DATETIME     |

### `tags`
| Column   | Type    |
|----------|---------|
| tagID    | INT (PK)|
| tagName  | VARCHAR |
| wifi     | VARCHAR |
| location | VARCHAR |
