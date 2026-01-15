# R-AISS Scout Console

**R-AISS Scout Console** is a dynamic match event logging dashboard built for real-time scouting and analysis. It allows scouts and analysts to digitize match events with precise pitch coordinates, manage match context, and export data for further analysis.

## Key Features

-   **Event Digitization**: Log technical actions (Pass, Shot, Tackle, etc.) with precise pitch coordinates on an interactive field.
-   **Live Match Management**: Track game time, periods (1st Half, 2nd Half), and team performance in real-time.
-   **Data Portability**: Instant export of match events to CSV format for integration with external analysis tools (Excel, Python, Tableau, etc.).
-   **Visual Feedback**: Real-time visualization of events on the pitch map.
-   **Mobile & Tablet Optimized**: Responsive design that works seamlessly on touch devices for pitch-side data collection.

## Usage

1.  **Setup Match**: Enter the match details (Date, Home Team, Away Team) in the setup modal.
2.  **Start Session**: The dashboard will load the pitch and control panel.
3.  **Log Events**:
    *   Select a **Team** (Home/Away).
    *   Select a **Player** from the grid.
    *   Select an **Action** (Pass, Dribble, Shot, etc.).
    *   Click on the **Pitch** to record the location of the event.
4.  **Export**: Use the "Settings / Export" button to download the session data as a CSV file.

## Technical Stack

-   **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
-   **Database**: Firebase Firestore (Configurable)
-   **Visualization**: HTML5 Canvas for pitch rendering

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/njugunakennedy/R-AISS-Scout-Console.git
    ```
2.  Open `index.html` in any modern web browser.

## Configuration

To enable cloud syncing, update the `firebaseConfig` object in `index.html` with your own Firebase project credentials.

```javascript
const firebaseConfig = {
    apiKey: "YOUR_API_KEY",
    authDomain: "your-project.firebaseapp.com",
    projectId: "your-project",
    storageBucket: "your-project.appspot.com",
    messagingSenderId: "YOUR_SENDER_ID",
    appId: "YOUR_APP_ID"
};
```

## License

This project is open-source and available for personal and educational use.
