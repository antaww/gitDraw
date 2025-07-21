# GitDraw

A Python application that allows you to create drawings in your GitHub contribution calendar by making commits on specific dates.

## Description

GitDraw enables you to create pixel art in your GitHub contribution graph by:
- Analyzing your GitHub contribution history
- Providing a graphical interface to design patterns
- Making commits on specific dates to form your desired drawing

## Features

- 📊 Fetch your GitHub contribution data via GraphQL API
- 🎨 Interactive GUI for creating drawings on a grid
- 📅 Calculate optimal date ranges for contribution calendar
- 🔄 Generate commits for specific dates to form patterns
- 🎯 Support for drawing on days without existing contributions

## Requirements

- Python 3.7+
- GitHub personal access token
- tkinter (usually included with Python)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/antaww/gitDraw.git
cd gitDraw
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your GitHub credentials:
```bash
cp .env.example .env
```
Edit `.env` and add your GitHub username and personal access token.

## Usage

1. Run the application:
```bash
python main.py
```

2. The application will:
   - Fetch your GitHub contribution data
   - Open a drawing interface
   - Allow you to create patterns by clicking on the grid
   - Generate commits for the selected dates

3. Use the drawing interface:
   - Click to draw pixels
   - Click and drag to draw multiple pixels
   - Click on drawn pixels to erase them
   - Click "Save and Quit" when finished

## Configuration

### GitHub Token

To use this application, you need a GitHub personal access token with the following permissions:
- `repo` (if working with private repositories)
- `user` (to read user contribution data)

Create your token at: https://github.com/settings/tokens

### Environment Variables

- `GITHUB_USERNAME`: Your GitHub username
- `GITHUB_TOKEN`: Your GitHub personal access token

## How It Works

1. **Data Fetching**: Uses GitHub's GraphQL API to retrieve your contribution calendar data
2. **Date Calculation**: Finds the optimal Sunday-to-Saturday date range for the contribution grid
3. **Drawing Interface**: Provides a tkinter-based GUI for creating pixel art
4. **Commit Generation**: Creates commits with specific dates to form your drawing

## Example

The application creates a 7×N grid representing days of the week over time:
- Each row represents a day of the week (Sunday to Saturday)
- Each column represents a week
- Filled pixels will result in commits on those dates

## Limitations

- Only works with days that have no existing contributions
- Requires a valid GitHub account and API access
- Changes your actual contribution history

## License

This project is for educational purposes. Use responsibly and be aware that it modifies your actual GitHub contribution history.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change. 