# IvANbot: Pokémon Edition

A Discord bot built with Python and discord.py that integrates the PokeAPI to provide a complete Pokémon management experience within Discord servers.

## Core Functionalities

*   **PokeAPI Integration**: Real-time data retrieval for Pokémon stats, types, and sprites.
*   **Persistent Team Storage**: User teams are saved in a local JSON database, ensuring data persists after bot restarts.
*   **Battle Simulation**: A combat system that calculates results based on base statistics and elemental type advantages.
*   **Slash Command Support**: Fully compatible with Discord's modern application command architecture.
*   **Automated Uptime**: Includes a Flask-based web server to maintain 24/7 connectivity on hosting platforms.

## Technical Stack

*   **Language**: Python 3.8+
*   **Primary Library**: discord.py
*   **API**: PokeAPI (REST)
*   **Data Format**: JSON
*   **Web Framework**: Flask (for keep-alive pings)

## Command Reference

| Command | Parameter | Function |
| :--- | :--- | :--- |
| `/poke` | `name` | Displays comprehensive Pokémon data and sprites. |
| `/catch` | `name` | Adds the specified Pokémon to the user's team. |
| `/team` | None | Lists the current user's team members. |
| `/vs` | `p1, p2` | Simulates a battle between two Pokémon. |
| `/swap` | `p1, p2` | Reorders Pokémon within the user's team. |
| `/remove` | `name` | Deletes a Pokémon from the user's team. |

## File Directory

*   `main.py`: Main application entry point and command definitions.
*   `server.py`: Background thread for HTTP server uptime.
*   `teams.json`: Local storage for user-specific team data.
*   `requirements.txt`: Project dependencies.
*   `PRIVACY_POLICY.md`: Documentation on data handling.
*   `TERMS_OF_SERVICE.md`: User agreement and usage rules.

## Setup Instructions

1. **Environment Configuration**: 
   Ensure you have a `.env` file with your `TOKEN`.
2. **Dependency Installation**:
   Execute `pip install -r requirements.txt`.
3. **Execution**:
   Run `python main.py`.

## Legal Notice

This project is an independent tool for educational use and is not affiliated with Nintendo or The Pokémon Company. All Pokémon assets are property of their respective owners.
