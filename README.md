# 🏗️ Consolidata - Washroom Design & Code Compliance

**Professional building code compliance and layout generation for Canadian jurisdictions**

![Consolidata](https://img.shields.io/badge/Consolidata-v1.0.0-green)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Overview

Consolidata is a comprehensive washroom design and building code compliance system that helps architects, engineers, and designers create compliant washroom layouts for Canadian building codes including NBC, Alberta, Ontario, and BC.

### ✨ Key Features

- **🏗️ Building Code Compliance** - Automated compliance checking for multiple Canadian jurisdictions
- **🎨 Layout Generator** - Intelligent 2D layout generation with proper clearances
- **📐 AutoCAD Export** - Professional drawings ready for construction documentation
- **♿ Accessibility Standards** - Full compliance with accessibility requirements
- **🔢 Fixture Calculations** - Accurate fixture requirements based on occupancy and building type
- **⚡ Real-time Updates** - Instant recalculation when parameters change

## 🚀 Quick Deploy

### One-Click Deployment

Deploy your own instance instantly:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template)
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone)
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy)

### Live Demo

🌐 **Try it now:** [consolidata-demo.railway.app](https://consolidata-demo.railway.app)

## 🚀 Local Development

### Prerequisites

- Python 3.8 or higher
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Installation & Setup

1. **Clone or Download** the project to your local machine
2. **Navigate** to the project directory:
   ```bash
   cd ConsolidataWashroomDesign
   ```
3. **Start the system** with one command:
   ```bash
   python start.py
   ```

The startup script will:
- ✅ Check and install required dependencies
- 🚀 Start the API server (port 5000)
- 🌐 Start the HTTP server (port 8000)
- 📚 Initialize the building codes database

### 🌐 Access the Application

Once started, access the application at:
- **Main Interface**: http://localhost:8000/frontend/index.html
- **System Test**: http://localhost:8000/tests/test_system.html
- **API Documentation**: http://localhost:5000/api/docs

## 📁 Project Structure

```
ConsolidataWashroomDesign/
├── frontend/                 # Frontend application
│   ├── index.html           # Main Consolidata interface
│   ├── styles.css           # Professional styling
│   └── script.js            # JavaScript functionality
├── backend/                 # Backend API server
│   └── app.py              # Flask API server
├── database/               # Database files
│   └── building_codes.db   # SQLite database (auto-created)
├── tests/                  # Testing utilities
│   └── test_system.html    # System test interface
├── deploy/                 # Deployment configurations
│   ├── railway.json        # Railway deployment
│   ├── vercel.json         # Vercel deployment
│   ├── render.yaml         # Render deployment
│   ├── netlify.toml        # Netlify deployment
│   └── docker/             # Docker configurations
├── docs/                   # Documentation
├── start.py               # Main startup script
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## 🌐 Deployment Options

### 🚄 Railway (Recommended)
- **Pros:** Easiest setup, automatic HTTPS, great free tier
- **Best for:** MVP, testing, small teams
- **Deploy:** Click the Railway button above

### 🎨 Render
- **Pros:** Reliable, good performance, professional features
- **Best for:** Production applications
- **Deploy:** See [deployment guide](deploy/DEPLOYMENT_GUIDE.md)

### ⚡ Vercel
- **Pros:** Global CDN, serverless, best performance
- **Best for:** Global scale applications
- **Deploy:** Click the Vercel button above

### 🐳 Docker
- **Pros:** Complete control, self-hosted
- **Best for:** Enterprise deployments
- **Deploy:** `cd deploy/docker && docker-compose up`

**📖 Full deployment guide:** [deploy/DEPLOYMENT_GUIDE.md](deploy/DEPLOYMENT_GUIDE.md)

## 🔧 API Endpoints

### Health Check
```http
GET /api/health
```

### Calculate Fixtures
```http
POST /api/calculate-fixtures
Content-Type: application/json

{
  "occupancy_load": 200,
  "building_type": "office",
  "jurisdiction": "NBC",
  "accessibility_level": "basic"
}
```

### Complete Analysis
```http
POST /api/complete-analysis
Content-Type: application/json

{
  "occupancy_load": 200,
  "building_type": "office",
  "jurisdiction": "NBC",
  "accessibility_level": "enhanced",
  "room_dimensions": {
    "length": 12.0,
    "width": 8.0,
    "height": 3.0
  }
}
```

## 🏛️ Supported Building Codes

- **🇨🇦 National Building Code (NBC)** - Complete 2020 compliance
- **🏔️ Alberta Building Code** - Provincial modifications
- **🍁 Ontario Building Code** - OBC specific requirements
- **🌲 BC Building Code** - British Columbia compliance

## 🏢 Supported Building Types

- **Office Buildings** - Commercial office spaces
- **Educational Facilities** - Schools and universities
- **Retail/Commercial** - Shopping centers and stores
- **Assembly Buildings** - Theaters, auditoriums, churches
- **Industrial Facilities** - Manufacturing and warehouses

## ♿ Accessibility Levels

- **Basic Compliance** - Minimum code requirements
- **Enhanced Accessibility** - Improved accessibility features
- **Universal Design** - Full universal design principles

## 🧪 Testing

### System Test
Access the system test interface at:
```
http://localhost:8000/tests/test_system.html
```

### Manual Testing
1. **Health Check**: Verify API is running
2. **Fixture Calculation**: Test fixture requirements
3. **Complete Analysis**: Test full system functionality

## 🛠️ Development

### Adding New Building Codes
1. Edit `backend/app.py`
2. Add new entries to the `populate_sample_data` method
3. Restart the system

### Customizing the Frontend
1. Edit `frontend/styles.css` for styling changes
2. Edit `frontend/script.js` for functionality changes
3. Edit `frontend/index.html` for structure changes

## 📊 Features in Detail

### Fixture Calculations
- Automatic calculation based on occupancy load
- Building type specific requirements
- Jurisdiction specific modifications
- Accessibility level adjustments

### Layout Generation
- 2D layout with proper spacing
- Clearance requirements
- Accessibility compliance
- Fixture positioning optimization

### Compliance Checking
- Real-time compliance scoring
- Detailed checklist generation
- Code reference citations
- Recommendation system

## 🔒 Security

- CORS enabled for frontend communication
- Input validation on all endpoints
- SQLite database with prepared statements
- No sensitive data storage
- Production security headers

## 📈 Performance

- Lightweight SQLite database
- Efficient API endpoints
- Responsive frontend design
- Fast calculation algorithms
- Global CDN support (Vercel/Netlify)

## 💰 Pricing

### Free Tiers Available
- **Railway:** 500 hours/month free
- **Render:** 750 hours/month free
- **Vercel:** 100GB bandwidth/month free
- **Netlify:** 100GB bandwidth/month free

### Paid Plans (if needed)
- **Railway:** $5/month unlimited
- **Render:** $7/month unlimited
- **Vercel:** $20/month team features
- **Netlify:** $19/month team features

## 🐛 Troubleshooting

### Common Issues

**API Server Won't Start**
- Check if port 5000 is available
- Verify Python dependencies are installed
- Check firewall settings

**Frontend Not Loading**
- Verify HTTP server is running on port 8000
- Check browser console for errors
- Ensure files are in correct directories

**Database Errors**
- Delete `database/building_codes.db` and restart
- Check file permissions
- Verify SQLite is available

### Getting Help

1. Check the system test page for diagnostics
2. Review browser console for JavaScript errors
3. Check terminal output for server errors
4. Verify all files are present and accessible
5. See [deployment guide](deploy/DEPLOYMENT_GUIDE.md) for platform-specific issues

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

## 📞 Support

For technical support or questions about building code compliance, please refer to the official building code documentation for your jurisdiction.

## 🌟 Roadmap

### Phase 2 Features
- [ ] 3D visualization
- [ ] AutoCAD DXF export
- [ ] Multi-room layouts
- [ ] Cost estimation
- [ ] Material specifications

### Phase 3 Features
- [ ] Mobile app
- [ ] Collaborative editing
- [ ] Project management
- [ ] Integration APIs
- [ ] Advanced reporting

---

**🏗️ Consolidata** - Professional washroom design made simple.

*Built with ❤️ for architects, engineers, and designers.*

**🚀 Ready to deploy?** Choose your platform above and go live in minutes! 