# OpenVis Universe 🌌

A stunning 3D visualization platform for exploring blockchain governance data, starting with Polkadot's OpenGov system. Experience governance relationships through immersive cosmic metaphors - from planetary systems to solar arrangements.

![OpenVis Universe](https://img.shields.io/badge/OpenVis-Universe-purple?style=for-the-badge)
![Three.js](https://img.shields.io/badge/Three.js-000000?style=for-the-badge&logo=three.js&logoColor=white)
![Neo4j](https://img.shields.io/badge/Neo4j-008CC1?style=for-the-badge&logo=neo4j&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)

## ✨ Features

### 🪐 Dual Cosmic Views
- **Planet System**: Proposals arranged on a central sphere with voters orbiting in concentric rings
- **Solar System**: Voters form the central sun with proposal planets orbiting by status

### 🎯 Interactive Elements
- **3D Navigation**: Smooth rotation, panning, and zooming
- **Dynamic Connections**: Real-time voting relationship lines (AYE/NAY/ABSTAIN)
- **Smart Tooltips**: Detailed information on hover
- **Status-Based Coloring**: Visual distinction by proposal status

### 🔧 Advanced Controls
- **View Mode Switching**: Seamless transitions between cosmic arrangements
- **Animation Controls**: Adjustable speed and particle density
- **Visibility Toggles**: Show/hide voters and connections
- **Auto-Rotate**: Automated exploration mode

### 📊 Complete Dataset Stats
- Total Proposals: 1,541
- Active Voters: 3,440
- Voting Relationships: 200,200

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Neo4j Aura DB account (for data extraction)
- Modern web browser with WebGL support

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/ss-deshmukh/OpenVIS-Universe.git
   cd OpenVIS-Universe
   ```

2. **Set up Python environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Start the visualization**
   ```bash
   python -m http.server 8000
   ```

4. **Open in browser**
   Navigate to `http://localhost:8000`

## 🗃️ Data Pipeline

### Neo4j Data Extraction
The project includes optimized data extractors for Neo4j Aura:

- `explore_schema.py` - Discover database structure
- `neo4j_data_extractor_optimized.py` - Batch data extraction
- `polkadot_voting_data.json` - Processed governance data

### Data Structure
```json
{
  "proposals": [...],     // Governance proposals with status
  "voters": [...],        // Active voter accounts
  "relationships": [...], // Voting connections
  "metadata": {...}       // Statistics and counts
}
```

## 🎮 Usage Guide

### Navigation Controls
- **Left-click + drag**: Rotate view
- **Right-click + drag**: Pan around
- **Scroll wheel**: Zoom in/out
- **Arrow keys**: Directional panning

### View Modes

#### 🪐 Planet System
- Proposals positioned on central sphere using latitude-longitude grid
- Status-based vertical sorting (Executed → Other → TimedOut → Rejected)
- Voters in equidistant concentric circles (80 per circle, 2× diameter spacing)

#### ☀️ Solar System
- Voters form central sun using spherical grid arrangement
- Proposals orbit as separate planets grouped by status
- Each planet contains proposals on its own spherical surface

### Visual Legend
- 🟢 **Green**: Executed proposals
- 🔵 **Blue**: Other status proposals  
- 🟠 **Orange**: Timed out proposals
- 🔴 **Red**: Rejected proposals
- ⚪ **White**: Active voters
- **Lines**: Voting connections (Green=AYE, Red=NAY, Yellow=ABSTAIN)

## 🏗️ Technical Architecture

### Frontend Stack
- **Three.js**: 3D rendering and scene management
- **OrbitControls**: Camera navigation
- **WebGL**: Hardware-accelerated graphics
- **Vanilla JavaScript**: Core application logic

### Data Processing
- **Neo4j Python Driver**: Database connectivity
- **Pandas**: Data manipulation and analysis
- **Batch Processing**: Memory-efficient data extraction

### Mathematical Precision
- **Spherical Coordinates**: Latitude-longitude grid positioning
- **Equidistant Spacing**: Optimal circle arrangements
- **Dynamic Scaling**: Size-based visual encoding

## 📁 Project Structure

```
openvis-universe/
├── index.html                          # Main visualization
├── polkadot_voting_data.json          # Governance data
├── neo4j_data_extractor_optimized.py  # Data extraction
├── requirements.txt                    # Python dependencies
├── README.md                          # Documentation
└── Helper Information/                # Additional resources
```

## 🔮 Future Roadmap

### Multi-Chain Support
- ✅ Polkadot OpenGov
- 🔄 Kusama (coming soon)
- 📋 Ethereum governance
- 📋 Cosmos ecosystem

### Enhanced Features
- 📋 Time-based animations
- 📋 Proposal filtering
- 📋 Voter clustering analysis
- 📋 Export capabilities

### Performance Optimizations
- 📋 WebGL2 rendering
- 📋 Level-of-detail (LOD)
- 📋 Streaming data updates

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Polkadot Community**: For the rich governance data
- **Three.js Team**: For the incredible 3D framework
- **Neo4j**: For graph database capabilities
- **Web3 Foundation**: For supporting decentralized governance

## 📞 Support

- 🐛 **Issues**: [GitHub Issues](https://github.com/ss-deshmukh/OpenVIS-Universe/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/ss-deshmukh/OpenVIS-Universe/discussions)
- 📧 **Email**: your.email@example.com

---

**Made with ❤️ for the decentralized future**

*Explore governance like never before - where data meets the cosmos* ✨
