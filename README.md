# Arena Brawl

A 2D multiplayer fighting game inspired by Super Smash Bros and Street Fighter, built with Python and JavaScript. Play online with up to 4 players!

## Features

- **2D Arena Combat**: Fast-paced fighting with combos and special abilities
- **Online Multiplayer**: Up to 4 players via WebSocket
- **4 Unique Characters**: Blaze, Tank, Shadow, and Storm
- **AI Bots**: Practice against AI opponents
- **Mobile Support**: Touch controls for mobile browsers
- **Power-ups & Health Boxes**: Tiered collectibles
- **Cop Mechanic**: Hide or take damage when cops appear!
- **Multiple Arenas**: Street, Rooftop, Warehouse, and Park

## Quick Start

### Local Development

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Run the server**:
```bash
python -m server.app
```

3. **Open in browser**:
```
http://localhost:5000
```

### Docker

```bash
# Development (just game server)
docker-compose up game

# Production (with nginx)
docker-compose up -d
```

## Controls

### Desktop (Keyboard)

| Action | Player 1 | Alternative |
|--------|----------|-------------|
| Move Left | A | ← |
| Move Right | D | → |
| Jump | W / Space | ↑ |
| Light Attack | J | Numpad 1 |
| Heavy Attack | K | Numpad 2 |
| Special | L | Numpad 3 |
| Block | Shift / S | Numpad 0 / ↓ |

### Mobile (Touch)
- **Left side**: Virtual D-pad for movement
- **Right side**: Action buttons (ATK, HVY, SPL, BLK)

## Characters

| Character | Style | Special Ability |
|-----------|-------|-----------------|
| **Blaze** | Aggressive | Fire Dash - Rapid gap closer |
| **Tank** | Defensive | Shield Block - 2.5x defense |
| **Shadow** | Evasive | Teleport - Short blink |
| **Storm** | Balanced | Lightning Strike - AoE damage |

## Game Mechanics

### Combat
- **Light Attack**: Fast, chains into combos
- **Heavy Attack**: Slow, high damage, ends combos
- **Special**: Unique ability with cooldown
- **Block**: 50% damage reduction
- **Combo**: Light → Light → Heavy

### Power-ups
- **Speed Boost** (Green): Move faster
- **Damage Boost** (Red): Deal more damage
- **Invincibility** (Gold): Temporary god mode

### Health Boxes
- **Common** (Brown): +15 HP, speed boost
- **Rare** (Silver): +35 HP, damage boost
- **Epic** (Gold): Full heal, invincibility

### Cop Mechanic
- Cops spawn randomly every 30-60 seconds
- 3-second warning siren before arrival
- Hide behind obstacles or take 25% HP damage

### Win Condition
- Last player standing wins
- 3 lives per player (Smash Bros style)
- 3-minute match timer

## Deployment (Hostinger VPS)

1. **Get VPS**: Ubuntu 22.04 on Hostinger

2. **Install Docker**:
```bash
curl -fsSL https://get.docker.com | sh
sudo apt install docker-compose
```

3. **Clone and deploy**:
```bash
git clone <your-repo> /opt/arena-brawl
cd /opt/arena-brawl
```

4. **Set environment**:
```bash
echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
```

5. **Configure SSL** (optional):
```bash
# Install certbot
sudo apt install certbot
sudo certbot certonly --standalone -d yourdomain.com

# Copy certs
mkdir ssl
sudo cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/
sudo cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/

# Uncomment SSL lines in nginx.conf
```

6. **Start**:
```bash
docker-compose up -d
```

## Project Structure

```
arena-brawl/
├── server/                 # Python backend
│   ├── app.py             # Flask entry point
│   ├── config.py          # Configuration
│   ├── game/              # Game engine
│   │   ├── engine.py      # Main loop
│   │   ├── physics.py     # Collision/gravity
│   │   ├── combat.py      # Attack system
│   │   └── events.py      # Cop/powerup spawns
│   ├── entities/          # Game objects
│   ├── ai/                # Bot system
│   ├── network/           # Multiplayer
│   └── maps/              # Arena definitions
├── static/                # Frontend
│   ├── index.html
│   ├── css/game.css
│   └── js/
│       ├── main.js        # Entry point
│       ├── game.js        # Canvas renderer
│       ├── input.js       # Controls
│       ├── network.js     # SocketIO client
│       └── ui.js          # UI manager
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── requirements.txt
```

## Tech Stack

- **Backend**: Python, Flask, Flask-SocketIO, Eventlet
- **Frontend**: HTML5 Canvas, JavaScript, Socket.IO
- **Deployment**: Docker, Nginx, Gunicorn

## License

MIT License - feel free to use and modify!

---

Made with love for Owen's Game project.
