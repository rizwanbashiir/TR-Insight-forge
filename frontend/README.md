# TR-InsightForge Frontend

A modern React-based Business Intelligence platform frontend built with Vite, Tailwind CSS, and Recharts.

## Features

- **Landing Page** - Marketing site with hero, features, pricing, and CTA sections
- **Authentication** - Sign in / Sign up with multi-step workspace creation
- **Dashboard** - KPI cards, revenue trends, sales distribution, regional performance, AI insights
- **Uploads** - Drag-and-drop file upload with dataset history
- **Forecasting** - ARIMA-based revenue forecasting with confidence intervals
- **Customer Segments** - RFM-based segmentation with cluster visualization
- **AI Chat** - Natural language data assistant with chat history
- **Team & Billing** - Workspace management, subscription, and team members

## Tech Stack

- React 18 + Vite
- React Router v6
- Tailwind CSS
- Recharts (charts)
- Lucide React (icons)
- PapaParse (CSV parsing)
- SheetJS (Excel parsing)
- React Dropzone (file upload)
- Axios (API calls)

## Getting Started

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

## Project Structure

```
frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── layout/        # Navbar, Sidebar, Footer
│   │   ├── upload/        # FileDropzone, FilePreview
│   │   ├── dashboard/     # KPICards, RevenueChart, CategoryChart, RegionChart
│   │   ├── forecast/      # ForecastChart, ForecastTable
│   │   ├── segmentation/  # SegmentPyramid, SegmentTable
│   │   ├── insights/      # AIReport
│   │   ├── landing/       # Hero, Features, Pricing, CTA, Footer
│   │   └── auth/          # SignInForm, SignUpForm
│   ├── pages/
│   ├── services/          # API services
│   ├── context/           # DataContext (React Context)
│   ├── hooks/             # Custom hooks
│   ├── utils/             # Parser, Formatter, Export
│   ├── routes/
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── package.json
├── tailwind.config.js
├── vite.config.js
└── .env
```

## Environment Variables

```
VITE_API_BASE_URL=http://localhost:5000/api
```

## Notes

- The app uses mock data for demo purposes. Connect to your backend API for real data.
- Authentication is simulated - in production, implement proper JWT token handling.
- The Ollama AI integration should be connected via the backend API.
