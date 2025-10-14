# 🎮 Satoshi's Arcade MCP

> **An arcade that learns from you — every move makes it smarter.**

A browser-based AI arcade showcasing the fusion of retro gameplay, blockchain-inspired data structures, and machine learning. Experience games like Ping-Pong and Tetris with AI opponents that adapt and learn from your gameplay patterns.

![Arcade Demo](https://img.shields.io/badge/Live%20Demo-🚀%20Play%20Now-blue?style=for-the-badge&logo=github)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge&logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-red?style=for-the-badge&logo=fastapi)
![AI](https://img.shields.io/badge/AI-Reinforcement%20Learning-purple?style=for-the-badge&logo=tensorflow)

## 🌟 Features

### 🎯 **AI-Powered Gameplay**
- **Adaptive AI**: Opponents learn from your moves and adapt difficulty
- **Reinforcement Learning**: AI improves through gameplay data
- **Model Context Protocol**: AI memory layer for contextual performance
- **Real-time Learning**: AI adjusts strategy during gameplay

### 🎮 **Retro Games**
- **🏓 Ping-Pong**: Classic paddle game with AI opponent
- **🧱 Tetris**: Block-stacking puzzle with AI analysis
- **🔊 Hard Bass Boom**: Epic sound effects with Web Audio API
- **📱 PWA Ready**: Play on mobile and desktop

### 🎨 **Immersive Design**
- **Neon-Bauhaus**: Glowing UI with IBM Plex Sans typography
- **Responsive Layout**: Works on iPhone, desktop, and tablets
- **Motion Effects**: Smooth animations and visual feedback
- **Dark Theme**: Easy on the eyes for extended play

### 🧠 **AI Architecture**
- **Modular Intelligence**: Easy to extend with new games
- **SQLite Database**: Lightweight storage for player data
- **Session Management**: Track gameplay across sessions
- **Performance Analytics**: Detailed AI learning metrics

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Modern web browser
- Git

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/polydeuces32/satoshis-arcade-mcp.git
cd satoshis-arcade-mcp
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Start the server**
```bash
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Open your browser**
```
http://localhost:8000
```

## 🎮 How to Play

### Ping-Pong
- **Move mouse** to control your paddle
- **Hit the ball** to score points
- **AI learns** from your paddle movements
- **First to 5 points** wins!

### Tetris
- **Arrow keys** to move and rotate pieces
- **Space** for hard drop
- **P** to pause
- **AI analyzes** your block placement efficiency

## 🏗️ Architecture

```
satoshis-arcade-mcp/
├── 🧠 ai/                    # AI intelligence engine
│   └── difficulty_agent.py   # Reinforcement learning agent
├── 🔌 api/                   # FastAPI backend
│   ├── main.py              # Application entry point
│   └── routes/              # Game API endpoints
│       ├── pingpong.py      # Ping-Pong game logic
│       ├── tetris.py        # Tetris game logic
│       └── leaderboard.py   # Score tracking
├── 🎨 frontend/              # Web interface
│   ├── arcade/              # Main menu
│   ├── pingpong/            # Ping-Pong game
│   ├── tetris/              # Tetris game
│   ├── manifest.json        # PWA configuration
│   └── service-worker.js    # Offline capabilities
├── 💾 database.py            # SQLite database management
├── 🚀 render.yaml            # Deployment configuration
└── 📦 requirements.txt       # Python dependencies
```

## 🧠 AI Learning System

### Reinforcement Learning
The AI uses a custom reinforcement learning algorithm that:
- **Observes** player behavior patterns
- **Adapts** difficulty based on performance
- **Learns** optimal strategies over time
- **Remembers** context across sessions

### Model Context Protocol (MCP)
- **Memory Layer**: Stores gameplay context and performance data
- **Replay Analysis**: Analyzes successful strategies
- **Cross-Session Learning**: AI remembers you between games
- **Performance Metrics**: Tracks learning progress

## 🎵 Sound System

### Hard Bass Boom Effects
- **Web Audio API**: Advanced audio synthesis
- **Multiple Oscillators**: Rich, layered bass sounds
- **Deep Frequencies**: 40Hz-200Hz range for maximum impact
- **Distortion & Reverb**: Epic, spacious sound design

### Sound Mapping
- **Hit Sounds**: Punchy paddle impacts
- **Score Sounds**: Deep celebration booms
- **Line Clear**: Epic Tetris completion sounds
- **Level Up**: Victory fanfare with multiple frequencies

## 🌐 Deployment

### Render.com (Recommended)
1. Connect your GitHub repository to Render
2. The `render.yaml` file will auto-configure deployment
3. Your arcade will be live at `https://your-app.onrender.com`

### Manual Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Start production server
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## 🔧 Development

### Adding New Games
1. Create game logic in `api/routes/`
2. Add frontend in `frontend/`
3. Integrate with AI system in `ai/difficulty_agent.py`
4. Update main menu in `frontend/arcade/`

### AI Customization
- Modify `ai/difficulty_agent.py` for different learning algorithms
- Adjust difficulty curves in game routes
- Add new performance metrics to database schema

## 📊 Performance Metrics

The AI tracks various metrics:
- **Win/Loss Ratios**: Overall performance
- **Reaction Times**: Player response speed
- **Strategy Patterns**: Common move sequences
- **Difficulty Progression**: Learning curve analysis

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🛣️ Roadmap

### Phase 1 ✅
- [x] Deploy Ping-Pong and Tetris
- [x] Implement AI learning system
- [x] Add sound effects
- [x] Create PWA functionality

### Phase 2 🚧
- [ ] Integrate Bitcoin/Stacks tokenization
- [ ] Add more games (Crypto Brick Breaker, Hash Puzzle Arena)
- [ ] Implement global leaderboards
- [ ] Add multiplayer functionality

### Phase 3 🔮
- [ ] Launch Satoshi's Arcade Network (SAN)
- [ ] Decentralized AI gaming protocol
- [ ] Cross-platform mobile apps
- [ ] NFT integration for achievements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **IBM Plex Sans** for the beautiful typography
- **FastAPI** for the robust backend framework
- **Web Audio API** for the epic sound system
- **SQLite** for lightweight data storage

## 🔗 Links

- **Live Demo**: [Play Now](https://satoshis-arcade-mcp.onrender.com)
- **GitHub**: [polydeuces32/satoshis-arcade-mcp](https://github.com/polydeuces32/satoshis-arcade-mcp)
- **Documentation**: [API Docs](https://satoshis-arcade-mcp.onrender.com/docs)

---

**Built with ❤️ by [Giancarlo Vizhnay](https://github.com/polydeuces32)**

*"The code you write makes you a programmer. The code you delete makes you a good one. The code you don't write makes you a great one."*
